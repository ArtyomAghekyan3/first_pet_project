
from openai import OpenAI
from config import settings

client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
)


def get_response_from_llm(content: str) -> str:
    response = client.chat.completions.create(
        model='deepseek-flash',
        max_tokens=500,
        extra_body={"thinking": {"type": "enabled"}},
        stream=False,
        reasoning_effort="high",
        messages=[{'role': 'system', 'content': 'You are a helpful assistant'}, 
                  {"role": "user", "content": content}]

    )
    print(response,
          response.choices[0].message.content,sep='\n'*5)
    return response