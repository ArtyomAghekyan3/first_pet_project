from typing import Annotated
from fastapi import APIRouter, Depends,File,UploadFile, HTTPException
from auth.dependencies import get_current_user
from database import   sessionDep,get_document_from_db,delete_document,get_documents_by_user
from moduls import  UsersModel
from rag.scripts.ingest import process_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/get_document/{document_id}")
def get_document(document_id: int,
                session: sessionDep,
                current_user: Annotated[
        UsersModel,
        Depends(get_current_user)
    ]):

    return get_document_from_db(document_id=document_id, session=session, user_id=current_user.id)


@router.delete("/delete_document/{document_id}",)
def delete_document_on_page(document_id: int, session: sessionDep,
                            current_user: Annotated[
                                                    UsersModel,
                                                    Depends(get_current_user)
                                                ]):
    return delete_document(document_id=document_id, session=session,user_id=current_user.id)

@router.post("/document_to_chunks")
def upload_document(
    
    session: sessionDep ,
    current_user: Annotated[
        UsersModel,
        Depends(get_current_user)],
    file: UploadFile = File(...),
    ):

    try:
        file_bytes = file.file.read()

        result = process_document(
            filename=file.filename,
            file_bytes=file_bytes,
            owner_id=current_user.id,
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

@router.get("/get_documents/")
def get_documents(
    session: sessionDep,
    current_user: Annotated[
        UsersModel,
        Depends(get_current_user)
    ]
):
    result=get_documents_by_user(session=session, user_id=current_user.id)
    
    return result

