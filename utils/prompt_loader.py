import os

def load_prompt(prompt_name: str) -> str:
    """
    Load the prompt text from the prompts folder based on the prompt name.
    """
    file_path = os.path.join("prompts", f"{prompt_name}.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
