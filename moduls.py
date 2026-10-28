from sqlalchemy.orm import  DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Text, func,DateTime,String,ForeignKey
from datetime import datetime


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


class DocumentsModel(Base):
    __tablename__='documents'


    id:Mapped[int]=mapped_column(primary_key=True)
    owner_id:Mapped[int]=mapped_column(ForeignKey(UsersModel.id, ondelete="CASCADE"),index=True)
    content:Mapped[str]=mapped_column(Text)
    title:Mapped[str]=mapped_column(String(128))
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
