from sqlalchemy.orm import  DeclarativeBase,Mapped,mapped_column,relationship
from sqlalchemy import Text, func,DateTime,String,ForeignKey
from datetime import datetime
from pgvector.sqlalchemy import VECTOR


class Base(DeclarativeBase):
    pass

class UsersModel(Base):
    __tablename__='users'


    id :Mapped[int]=mapped_column(primary_key=True)
    email :Mapped[str]=mapped_column(String(255),unique=True,index=True)
    firstname:Mapped[str]=mapped_column(String(100))
    lastname:Mapped[str]=mapped_column(String(100))
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),)
    hashed_password :Mapped[str]
    sex:Mapped[str]=mapped_column(String(10),default='male',server_default='male')

    documents:Mapped[list["DocumentsModel"]]=relationship(back_populates="user",cascade="all, delete-orphan")


class DocumentsModel(Base):
    __tablename__='documents'


    id:Mapped[int]=mapped_column(primary_key=True)
    owner_id:Mapped[int]=mapped_column(ForeignKey(UsersModel.id, ondelete="CASCADE"),index=True)
    content: Mapped[str | None] = mapped_column(Text)
    title:Mapped[str]=mapped_column(String(128))
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    user:Mapped["UsersModel"]=relationship(back_populates="documents")

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(index=True)
    role: Mapped[str]
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey(DocumentsModel.id, ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    chunk_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    embedding: Mapped[list[float]] = mapped_column(
    VECTOR(1024)
)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    document: Mapped["DocumentsModel"] = relationship(back_populates="chunks")