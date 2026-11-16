
from moduls import DocumentsModel
from moduls import ChunkModel
from ..file_changer import extract_text
from ..chunking import chunk_text
from ..embeddings import embed_texts
import hashlib
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

def process_document(filename, file_bytes, owner_id, session):
    h = hashlib.sha256(file_bytes).hexdigest()

    def find_existing():
        return session.scalar(select(DocumentsModel.id).where(
            DocumentsModel.owner_id == owner_id, DocumentsModel.content_hash == h))

    existing = find_existing()
    session.commit()
    if existing is not None:
        return {"document_id": existing, "filename": filename, "status": "already_exists"}

    text = extract_text(filename, file_bytes)
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    if not chunks:
        raise ValueError("Документ пустой")
    embeddings = embed_texts([c["content"] for c in chunks])
    if len(chunks) != len(embeddings):
        raise RuntimeError("Chunks and embeddings count mismatch")

    try:
        document = DocumentsModel(owner_id=owner_id, title=filename[:128],
                                  content=text, content_hash=h)
        session.add(document)
        session.flush()
        session.add_all([
            ChunkModel(document_id=document.id, content=c["content"],
                       chunk_id=f"{document.id}:{c['index']}", embedding=e)
            for c, e in zip(chunks, embeddings)
        ])
        session.commit()
    except IntegrityError:
        session.rollback()
        return {"document_id": find_existing(), "filename": filename, "status": "already_exists"}
    except Exception:
        session.rollback()
        raise

    return {"document_id": document.id, "filename": filename,
            "chunks_created": len(chunks), "status": "created"}