import asyncio
import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from database import new_session  # замените на ваш фабричный генератор/сессию AsyncSession
from llm import stream_response_from_llm


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def evaluate_item(
    item: dict[str, Any],
    actual_answer: str,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    expected_answer = item.get("reference_answer", "")
    expected_doc = item.get("doc_title")

    norm_ref = normalize_text(expected_answer)
    norm_actual = normalize_text(actual_answer)
    answer_contains_ref = bool(norm_ref and norm_ref in norm_actual)

    cited_docs = [str(s.get("document", "")) for s in sources]
    doc_hit = None
    if expected_doc:
        doc_hit = any(expected_doc == doc or expected_doc in doc for doc in cited_docs)

    return {
        "answer_contains_ref": answer_contains_ref,
        "doc_hit": doc_hit,
        "cited_docs": cited_docs,
    }


async def run_single_question(
    item: dict[str, Any],
    owner_id: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    q_id = item["id"]
    question = item["question"]
    session_id = f"eval_q{q_id}_{uuid4().hex[:8]}"

    content_parts: list[str] = []
    sources: list[dict[str, Any]] = []
    usage_data: dict[str, Any] = {}

    start = time.perf_counter()
    async with semaphore:
        try:
            with new_session() as session:
                async for kind, data in stream_response_from_llm(
                    session_id=session_id,
                    content=question,
                    session=session,
                    owner_id=owner_id,
                    limit=5,
                ):
                    if kind == "content":
                        # В SSE-роутере data уходит как JSON-строка; внутри stream_response_from_llm это str
                        content_parts.append(
                            json.loads(data) if isinstance(data, str) and data.startswith('"') else str(data)
                        )
                    elif kind == "sources":
                        sources = json.loads(data) if isinstance(data, str) else (data or [])
                    elif kind == "usage":
                        usage_data = json.loads(data) if isinstance(data, str) else (data or {})

            elapsed = round(time.perf_counter() - start, 3)
            actual_answer = "".join(content_parts).strip()
            metrics = evaluate_item(item, actual_answer, sources)

            return {
                "id": q_id,
                "type": item.get("type"),
                "question": question,
                "doc_title": item.get("doc_title"),
                "evidence": item.get("evidence"),
                "reference_answer": item.get("reference_answer"),
                "actual_answer": actual_answer,
                "sources": sources,
                "usage": usage_data,
                "latency_sec": elapsed,
                "status": "ok",
                "error": None,
                **metrics,
            }
        except Exception as exc:
            elapsed = round(time.perf_counter() - start, 3)
            return {
                "id": q_id,
                "type": item.get("type"),
                "question": question,
                "doc_title": item.get("doc_title"),
                "evidence": item.get("evidence"),
                "reference_answer": item.get("reference_answer"),
                "actual_answer": "".join(content_parts).strip(),
                "sources": sources,
                "usage": usage_data,
                "latency_sec": elapsed,
                "status": "error",
                "error": str(exc),
                "answer_contains_ref": False,
                "doc_hit": False if item.get("doc_title") else None,
                "cited_docs": [str(s.get("document", "")) for s in sources],
            }


def print_report(rows: list[dict[str, Any]]) -> None:
    ok_rows = [r for r in rows if r["status"] == "ok"]
    if not rows:
        print("Нет результатов для отчёта.")
        return

    avg_latency = sum(r["latency_sec"] for r in ok_rows) / len(ok_rows) if ok_rows else 0.0
    total_tokens = sum(r.get("usage", {}).get("total_tokens", 0) for r in ok_rows)
    ref_hits = sum(1 for r in ok_rows if r.get("answer_contains_ref"))

    doc_rows = [r for r in ok_rows if r.get("doc_hit") is not None]
    doc_hits = sum(1 for r in doc_rows if r.get("doc_hit"))

    print("\n=== Итоги оценки RAG ===")
    print(f"Успешно выполнено: {len(ok_rows)}/{len(rows)}")
    print(f"Среднее время ответа: {avg_latency:.2f} с")
    print(f"Суммарно токенов: {total_tokens}")
    if ok_rows:
        print(f"Вхождение reference_answer: {ref_hits}/{len(ok_rows)}")
    if doc_rows:
        print(f"Попадание в doc_title (среди цитируемых sources): {doc_hits}/{len(doc_rows)}")


async def main(
    questions_path: str = "evals/questions.json",
    output_path: str = "evals/results.json",
    owner_id: int = 1,
    concurrency: int = 2,
    resume: bool = True,
) -> None:
    raw = json.loads(Path(questions_path).read_text(encoding="utf-8"))
    # Поддерживаем как список [...], так и одиночный объект {...}
    questions = raw if isinstance(raw, list) else [raw]

    out_file = Path(output_path)
    results_by_id: dict[Any, dict[str, Any]] = {}

    if resume and out_file.exists():
        existing = json.loads(out_file.read_text(encoding="utf-8"))
        for row in existing:
            if row.get("status") == "ok":
                results_by_id[row["id"]] = row

    pending = [q for q in questions if not (resume and q["id"] in results_by_id)]
    semaphore = asyncio.Semaphore(concurrency)

    print(f"Всего вопросов: {len(questions)}. Запускаем: {len(pending)} (concurrency={concurrency}).")

    tasks = [asyncio.create_task(run_single_question(q, owner_id, semaphore)) for q in pending]
    for coro in asyncio.as_completed(tasks):
        record = await coro
        results_by_id[record["id"]] = record

        ordered = [results_by_id[q["id"]] for q in questions if q["id"] in results_by_id]
        out_file.write_text(
            json.dumps(ordered, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(
            f"[id={record['id']}] status={record['status']} "
            f"doc_hit={record.get('doc_hit')} ref_hit={record.get('answer_contains_ref')} "
            f"time={record['latency_sec']}s"
        )

    final_rows = [results_by_id[q["id"]] for q in questions if q["id"] in results_by_id]
    print_report(final_rows)


if __name__ == "__main__":
    asyncio.run(main())