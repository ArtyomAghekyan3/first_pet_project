import json
from collections import defaultdict

from sqlalchemy import select

from database import new_session        
from moduls import ChunkModel, DocumentsModel
from rag.retrieval import search_similar_chunks 

QUOTES = str.maketrans({"«": '"', "»": '"', "“": '"', "”": '"', "„": '"',
                        "–": "-", "—": "-", "−": "-"})


def norm(s: str) -> str:
    s = s.casefold().replace("ё", "е").translate(QUOTES)
    return " ".join(s.split())


def norm_quote(s: str) -> str:
    return norm(s).rstrip(".,;: ")  # финальная пунктуация часто расходится


def requirements(q) -> list[tuple[str, str]]:
    ev = q["evidence"]
    if isinstance(ev, str):
        return [(q["doc_title"], norm_quote(ev))]
    if isinstance(ev, list) and all(isinstance(x, dict) for x in ev):
        return [(x["doc_title"], norm_quote(x["quote"])) for x in ev]
    raise ValueError(f"Неизвестный формат evidence у вопроса {q['id']}")


def load_chunks(session, owner_id) -> dict[str, list[str]]:
    stmt = (
        select(DocumentsModel.title, ChunkModel.content)
        .join(ChunkModel.document)
        .where(DocumentsModel.owner_id == owner_id)
    )
    by_title = defaultdict(list)
    for title, content in session.execute(stmt):
        by_title[title].append(norm(content))
    return by_title


def run_eval(owner_id: int, path="evals/questions.json", k=3):
    questions = json.load(open(path, encoding="utf-8"))
    single, multi = [], []  # ранги по каждому вопросу
    chunking_fail, retrieval_fail, skipped = [], [], []

    with new_session() as session:
        chunks_by_title = load_chunks(session, owner_id)

        for q in questions:
            reqs = requirements(q)
            if not reqs:
                skipped.append(q["id"])  # вопросы без ответа в документах
                continue

            # 1) есть ли каждая цитата хоть в одном чанке в БД
            missing = [
                t for t, quote in reqs
                if not any(quote in c for c in chunks_by_title.get(t, []))
            ]
            if missing:
                chunking_fail.append((q["id"], missing))
                continue

            # 2) где в выдаче находится каждая цитата
            result = search_similar_chunks(session, q["question"], owner_id, limit=3)
            ranks = []
            for t, quote in reqs:
                ranks.append(next(
                    (i for i, (chunk, _) in enumerate(result, 1)
                     if chunk.document.title == t and quote in norm(chunk.content)),
                    None,
                ))
            if any(r is None for r in ranks):
                retrieval_fail.append((q["id"], ranks))
            (single if len(reqs) == 1 else multi).append(ranks)

    print(f"Пропущено без evidence: {skipped}")
    print(f"Чанкинг/текст (цитаты нет в БД): {chunking_fail}\n")

    if single:
        r = [x[0] for x in single]
        n = len(r)
        print(f"== Обычные вопросы: {n} (только те, где цитата есть в БД) ==")
        print(f"Hit@1: {sum(x == 1 for x in r) / n:.0%}")
        print(f"Hit@{k}: {sum(x is not None for x in r) / n:.0%}")
        print(f"MRR:   {sum(1 / x for x in r if x) / n:.2f}")

    if multi:
        n = len(multi)
        print(f"\n== Multi-hop: {n} ==")
        print(f"Все куски в топ-{k}: "
              f"{sum(all(x is not None for x in rs) for rs in multi) / n:.0%}")
        print(f"Хотя бы один кусок на 1-м месте: "
              f"{sum(1 in rs for rs in multi) / n:.0%}")

    print(f"\nЧанк есть, но поиск не нашёл (id, ранги): {retrieval_fail}")


if __name__ == "__main__":
    run_eval(owner_id=1)