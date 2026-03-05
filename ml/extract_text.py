"""Extract text from PDF and DOCX files."""
from pathlib import Path


def extract_from_pdf(file_path):
    """Extract text from PDF file."""
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        raise ValueError(f"Could not extract text from PDF: {e}")


def extract_from_docx(file_path):
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Could not extract text from DOCX: {e}")


def extract_text_from_file(file_path_or_obj):
    """
    Extract text from file. Supports PDF and DOCX.
    file_path_or_obj: path string, Path, or Django UploadedFile.
    """
    if hasattr(file_path_or_obj, "read"):
        import tempfile
        suffix = Path(file_path_or_obj.name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in file_path_or_obj.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        try:
            if suffix == ".pdf":
                return extract_from_pdf(tmp_path)
            elif suffix in (".docx", ".doc"):
                return extract_from_docx(tmp_path)
            else:
                raise ValueError(f"Unsupported file type: {suffix}. Use PDF or DOCX.")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    path = Path(file_path_or_obj)
    if not path.exists():
        raise FileNotFoundError(str(path))

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_from_pdf(path)
    elif suffix in (".docx", ".doc"):
        return extract_from_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use PDF or DOCX.")
