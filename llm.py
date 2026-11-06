from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
)


async def stream_response_from_llm(content: str):
    stream = await client.chat.completions.create(
        model="deepseek-flash",  
        max_tokens=500,
        extra_body={"thinking": {"type": "enabled"}},
        reasoning_effort="high",
        stream=True,
        stream_options={"include_usage": True},
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": content},
        ],
    )
    async for chunk in stream:
        if not chunk.choices:  
            if chunk.usage:
                
                yield "usage", chunk.usage.model_dump()
            continue
        delta = chunk.choices[0].delta
        reasoning = getattr(delta, "reasoning_content", None)
        if reasoning:
            yield "reasoning", reasoning
        elif delta.content:
            yield "content", delta.content