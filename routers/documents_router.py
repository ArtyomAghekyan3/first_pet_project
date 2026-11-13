from fastapi import APIRouter,File,UploadFile, HTTPException
from database import   sessionDep,get_document_from_db,create_document,delete_document,get_documents_by_user
from rag.scripts.ingest import process_document

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

@router.get("/get_documents_by_user/{user_id}")
def get_documents_by_user_endpoint(user_id: int, session: sessionDep):
    return get_documents_by_user(user_id=user_id, session=session)

@router.post("/document_to_chunks")
def upload_document(
    owner_id: int,
    session: sessionDep ,
    file: UploadFile = File(...),
    
):

    try:
        file_bytes = file.file.read()

        result = process_document(
            filename=file.filename,
            file_bytes=file_bytes,
            owner_id=owner_id,
            session=session
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

    finally:
        file.file.close()

