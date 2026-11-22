from rag.sys_prompt import prompt
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
import re
from config import settings
from history import get_history, save_exchange
from rag.retrieval import search_similar_chunks
import time



client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
)


CITATION_RE = re.compile(r"\[(\d+)\]")

system_prompt = prompt

async def stream_response_from_llm(
    session_id: str,
    content: str,
    session: AsyncSession,
    owner_id: int
):
    start = time.perf_counter()

    # 1. Получаем историю диалога
    history = await get_history(session_id, owner_id=owner_id, limit=5)

    # 2. Ищем похожие чанки в PostgreSQL
    chunks =  search_similar_chunks(
        session=session,
        query=content,
        limit=5,
        owner_id=owner_id
    )

    # 3. Формируем контекст из найденных чанков
    context_parts = []

    for chunk, similarity in chunks:
        context_parts.append(
            f"""
            Document ID: {chunk.document_id}
            Chunk ID: {chunk.id}
            Similarity: {similarity:.4f}
            Content:
            {chunk.content}
            """
        )

    context = "\n\n".join(context_parts)

    # 4. Формируем сообщения для DeepSeek
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        *history,
        {
            "role": "user",
            "content": f"""
            Document context:

            {context if context else "No relevant documents found."}

            User question:

            {content}
            """,
        },
    ]

    answer_parts: list[str] = []

    # 5. Запускаем потоковую генерацию
    stream = await client.chat.completions.create(
        model="deepseek-flash",
        max_tokens=4000,
        extra_body={"thinking": {"type": "enabled"}},
        reasoning_effort="high",
        stream_options={"include_usage": True},
        stream=True,
        messages=messages,
    )

    # 6. Получаем ответ частями
    async for chunk in stream:

        if chunk.usage is not None:
            elapsed = time.perf_counter() - start
            u = chunk.usage

            with open("notes/llm_usage.log", "a") as f:
                f.write(
                    f"LLM usage: "
                    f"prompt={u.prompt_tokens} "
                    f"completion={u.completion_tokens} "
                    f"total={u.total_tokens} "
                    f"time={elapsed:.2f}s\n"
                )

            yield "usage", chunk.usage.model_dump()

        if chunk.choices:
            delta = chunk.choices[0].delta
            if delta.content:
                answer_parts.append(delta.content)

                yield "content", delta.content

    # 7. Собираем полный ответ
    answer = "".join(answer_parts)


    # 8. Источники: только реально процитированные и существующие номера
    cited = {int(n) for n in CITATION_RE.findall(answer)}
    sources = [
        {
            "ref": i,
            "document_id": chunk.document_id,
            "document": chunk.document.title,
            "chunk_index": chunk.chunk_id,
            
            #"similarity": round(similarity, 4),
        }
        for i, (chunk, similarity) in enumerate(chunks, start=1)
        if i in cited
    ]
    yield "sources", sources

    # 9. В историю сохраняем ответ без ссылок [n]
    if answer:
        clean_answer = re.sub(r"\s*\[\d+\]", "", answer)
        await save_exchange(session_id, content, clean_answer, owner_id=owner_id)