from io import BytesIO, StringIO
from pathlib import Path

from pypdf import PdfReader
from docx import Document
import csv


def extract_text(filename: str, file_bytes: bytes) -> str:

    extension = Path(filename).suffix.lower()

    if extension == ".txt" or extension == ".md":
        text = file_bytes.decode("utf-8-sig")

    elif extension == ".pdf":
        reader = PdfReader(BytesIO(file_bytes))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif extension == ".docx":
        document = Document(BytesIO(file_bytes))

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )
    elif extension == ".csv":
        csv_text = file_bytes.decode("utf-8-sig")

        reader = csv.reader(StringIO(csv_text))

        rows = []

        for row in reader:
            rows.append(" | ".join(row))

        text = "\n".join(rows)

    else:
        raise ValueError("Unsupported file format")

    text = text.strip()

    if not text:
        raise ValueError("File contains no extractable text")

    return text