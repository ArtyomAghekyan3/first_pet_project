from openai import AsyncOpenAI
from config import settings
import time



client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
)

system_prompt="You are a helpful assistant"
async def stream_response_from_llm(content: str):
    start = time.perf_counter()
    stream = await client.chat.completions.create(
        model="deepseek-flash",  
        max_tokens=500,
        extra_body={"thinking": {"type": "enabled"}},
        reasoning_effort="high",
        stream_options={"include_usage": True},
        
        stream=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
    )

    async for chunk in stream:   

        if chunk.usage is not None:
                        elapsed = time.perf_counter() - start
                        u = chunk.usage

                        with open('llm_usage.log', 'a') as f:
                            f.write(
                                f"LLM usage: prompt={u.prompt_tokens} completion={u.completion_tokens} total={u.total_tokens} time={elapsed:.2f}s\n"
                            )
                        yield "usage", chunk.usage.model_dump()
           
        
        if  chunk.choices:  
            
            delta = chunk.choices[0].delta
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                yield "reasoning", reasoning
            elif delta.content:
                yield "content", delta.content