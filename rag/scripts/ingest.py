from sqlalchemy.orm import Session

from moduls import DocumentsModel
from moduls import ChunkModel

from ..file_changer import extract_text
from ..chunking import chunk_text
from ..embeddings import embed_texts


def process_document(
    filename: str,
    file_bytes: bytes,
    owner_id: int,
    session: Session
):

    try:
        
        text = extract_text(filename, file_bytes)

       
        document = DocumentsModel(
            owner_id=owner_id,
            title=filename[:128],
            content=text
        )

        session.add(document)

      
        session.flush()

       
        chunks = chunk_text(
            text,
            chunk_size=800,
            overlap=100
        )

       
        contents = [
            chunk["content"]
            for chunk in chunks
        ]

       
        embeddings = embed_texts(contents)

       
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch")

        
        db_chunks = []

        for chunk, embedding in zip(chunks, embeddings):

            db_chunk = ChunkModel(
                document_id=document.id,
                content=chunk["content"],
                chunk_id=f"{document.id}:{chunk['index']}",
                embedding=embedding
            )

            db_chunks.append(db_chunk)

       
        session.add_all(db_chunks)

        
        session.commit()

        session.refresh(document)

        return {
            "document_id": document.id,
            "filename": filename,
            "chunks_created": len(db_chunks),
            "status": "success"
        }

    except Exception:
        session.rollback()
        raise