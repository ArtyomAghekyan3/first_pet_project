
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

from llm import stream_response_from_llm
from schems import llmContentSchems
from database import sessionDep


router = APIRouter(
    prefix="/llm",
    tags=["api"]
)


@router.post(
    "/get_response",
    response_class=EventSourceResponse
)
async def get_llm_response(
    content: llmContentSchems,
    session: sessionDep,
):
    async for kind, data in stream_response_from_llm(
        session_id=content.session_id,
        content=content.content,
        session=session,
    ):
        yield ServerSentEvent(
            event=kind,
            data=data
        )
