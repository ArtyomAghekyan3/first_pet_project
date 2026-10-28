from fastapi import APIRouter
from database import  get_documents, get_user,sessionDep,get_document_from_db,create_document,delete_document
router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/get_document/{document_id}")
def get_document(document_id: int, session: sessionDep):
    return get_document_from_db(document_id=document_id, session=session)


@router.post("/create_document")
def create_document_on_page(title: str, session: sessionDep, owner_id: int, content: str | None = None):
    return create_document(title=title, content=content, owner_id=owner_id, session=session)

@router.delete("/delete_document/{document_id}")
def delete_document_on_page(document_id: int, session: sessionDep):
    return delete_document(document_id=document_id, session=session)

@router.get("/get_documents")
def get_documents_on_page(session: sessionDep):
    return get_documents(session=session)

    

