import io
import PyPDF2
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text.strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    name_lower = filename.lower()
    if name_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name_lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name_lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        try:
            return extract_text_from_pdf(file_bytes)
        except Exception:
            return file_bytes.decode("utf-8", errors="ignore")
