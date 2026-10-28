from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker ,Session
from config import settings
from moduls import Base,UsersModel,DocumentsModel
from typing import Annotated
from fastapi import Depends, HTTPException
from security import hash_password_func


engine=create_engine(settings.database_url,echo=True)

new_session=sessionmaker(engine,expire_on_commit=False)


def create_db():
    engine.echo=False
    Base.metadata.drop_all(engine,checkfirst=True)
    Base.metadata.create_all(engine)
    engine.echo=False

        
def get_db():
    with new_session() as session:
        yield session


sessionDep=Annotated[Session, Depends(get_db)]


def create_user(email:str,firstname:str,lastname:str,hashed_password:str,session:sessionDep):
    query=select(UsersModel).filter(UsersModel.email==email)
    if session.execute(query).scalars().first():
        raise HTTPException(status_code=409, detail="Email already exists")
    hashed_password=hash_password_func(hashed_password)
  
    user=UsersModel(
                email=email,
                firstname=firstname,
                lastname=lastname,
                hashed_password=hashed_password
        )
    session.add(user)
    session.commit()
    return user

    
def get_user(user_id: int,session:sessionDep):
    
    query=select(UsersModel).where(UsersModel.id==user_id)
    user=session.execute(query).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

    
def delete_user(user_id: int,session:sessionDep):
    
    query=select(UsersModel).where(UsersModel.id==user_id)
    user=session.execute(query).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message":"User deleted successfully","user_id":user_id}

    
def update_user(user_id: int, data: dict, session: sessionDep):
    user = get_user(user_id=user_id, session=session)
    for field, value in data.items():
        setattr(user, field, value)
    session.commit()
    return user

def get_document_from_db(document_id: int, session: sessionDep):
    query = select(DocumentsModel).where(DocumentsModel.id == document_id)
    document = session.execute(query).scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

def create_document(title: str, content: str, owner_id: int, session: sessionDep):
    document = DocumentsModel(title=title, content=content, owner_id=owner_id)
    session.add(document)
    session.commit()
    return document

def delete_document(document_id: int, session: sessionDep):
    query = select(DocumentsModel).where(DocumentsModel.id == document_id)
    document = session.execute(query).scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(document)
    session.commit()
    return {"message": "Document deleted successfully", "document_id": document_id}


def get_documents(session: sessionDep):
    query = select(DocumentsModel)
    documents = session.execute(query).scalars().all()
    return documents