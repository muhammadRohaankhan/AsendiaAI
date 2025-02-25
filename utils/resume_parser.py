from utils.text_cleaner import clean_text
from utils.llm_utils import extract_candidate_info
from utils.file_converter import convert_file_to_text

def parse_resume(file_path: str) -> dict:
    """
    Parse a resume by converting it to text and cleaning it.
    This version uses PyPDF2 (or other converters) to extract all text without calling an LLM.
    Returns a dictionary with:
      - "id": a unique identifier (using the filename)
      - "text": the full cleaned resume text
    """
    text = convert_file_to_text(file_path)
    text = clean_text(text)
    return {
        "id": file_path.split("/")[-1],  # use the filename as a unique id for simplicity
        "text": text
    }