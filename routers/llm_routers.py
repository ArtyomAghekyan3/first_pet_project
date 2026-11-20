
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent

from auth.dependencies import get_current_user
from llm import stream_response_from_llm
from moduls import UsersModel
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
    current_user: Annotated[
        UsersModel,
        Depends(get_current_user)
    ]):
    async for kind, data in stream_response_from_llm(
        session_id=content.session_id,
        content=content.content,
        session=session,
        owner_id=current_user.id
        
    ):
        yield ServerSentEvent(
            event=kind,
            data=data
        )
