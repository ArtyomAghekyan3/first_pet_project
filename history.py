import asyncio
from sqlalchemy import select

from database import new_session  
from moduls import ChatMessageModel


def _get_history(session_id: str, owner_id: int, limit: int) -> list[dict]:
    with new_session() as db:
        rows = db.execute(
            select(ChatMessageModel.role, ChatMessageModel.content)
            .where(ChatMessageModel.session_id == session_id)
            .where(ChatMessageModel.owner_id == owner_id)
            .order_by(ChatMessageModel.id.desc())
            .limit(limit)
        ).all()
   
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def _save_exchange(session_id: str, user_text: str, answer: str, owner_id: int) -> None:
    with new_session() as db:
        db.add_all([
            ChatMessageModel(session_id=session_id, role="user", content=user_text, owner_id=owner_id),
            ChatMessageModel(session_id=session_id, role="assistant", content=answer, owner_id=owner_id),
        ])
        db.commit()


async def get_history(session_id: str, owner_id: int, limit: int = 20) -> list[dict]:
    return await asyncio.to_thread(_get_history, session_id, owner_id, limit)


async def save_exchange(session_id: str, user_text: str, answer: str, owner_id: int) -> None:
    await asyncio.to_thread(_save_exchange, session_id, user_text, answer, owner_id)