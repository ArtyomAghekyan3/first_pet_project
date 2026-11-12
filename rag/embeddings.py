from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  

def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = _model.encode(texts, normalize_embeddings=True, batch_size=32)
    return vectors.tolist()