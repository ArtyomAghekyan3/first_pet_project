

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть > 0")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap должен быть >= 0 и < chunk_size")

    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        piece = text[start:start + chunk_size].strip()
        if piece:
            chunks.append({
                "index": len(chunks),
                "start_char": start,
                "content": piece,
            })
        if start + chunk_size >= len(text):
            break
    return chunks