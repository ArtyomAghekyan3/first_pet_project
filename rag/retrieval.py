from .embeddings import embed_texts
from moduls import ChunkModel, DocumentsModel
from sqlalchemy import select
from sqlalchemy.orm import Session



def search_similar_chunks(
    session: Session,
    query: str,
    owner_id: int,
    limit: int = 3,
    
):
    # 1. Создаём embedding пользовательского вопроса
    query_embedding = embed_texts([query])[0]

    # 2. Вычисляем cosine distance
    distance = ChunkModel.embedding.cosine_distance(
        query_embedding
    )

    # 3. Создаём SQL-запрос
    stmt = (
        select(
            ChunkModel,
            distance.label("distance")
        )
        .join(ChunkModel.document)
        .where(DocumentsModel.owner_id == owner_id)
        .order_by(distance.asc())
        .limit(limit)
    )


    # 4. Выполняем запрос
    result = session.execute(stmt).all()
    for row in result:
        chunk, distance_value = row
        print(f"Chunk ID: {chunk.id}, Document: {chunk.document.title}, Distance: {1-distance_value}")

    # 5. Возвращаем найденные чанки
    return result