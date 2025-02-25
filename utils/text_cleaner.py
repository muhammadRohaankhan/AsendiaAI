import re

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and unwanted characters.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
