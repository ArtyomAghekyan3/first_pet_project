from fastapi import APIRouter
from llm import get_response_from_llm
from schems import llmContentSchems


router = APIRouter(prefix="/llm", tags=["api"])

@router.post("/get_response")
def get_llm_response(content: llmContentSchems):
    llm_response = get_response_from_llm(content.content)
    return {"response": llm_response.choices[0].message.content}