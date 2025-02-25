import os
import PyPDF2
import docx

def convert_file_to_text(file_path: str) -> str:
    """
    Convert a resume file (PDF, DOCX, or plain text) to text.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return pdf_to_text(file_path)
    elif ext in ['.docx', '.doc']:
        return docx_to_text(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

def pdf_to_text(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def docx_to_text(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    """
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
