from utils.llm_client import send_openai_request
from utils.prompt_loader import load_prompt
from utils.config import load_config

# Load API key from configuration
config = load_config()
API_KEY = config.get("openai_api_key")

def extract_candidate_info(text: str) -> dict:
    """
    Extract candidate information from resume text using OpenAI.
    Loads a detailed prompt that instructs the model to extract data following a relational database schema.
    """
    prompt = load_prompt("extract_candidate_info")
    response = send_openai_request(text, prompt, API_KEY)
    return response

def expand_query(query: str) -> dict:
    """
    Expand the recruiter query to include synonyms or related terms using OpenAI.
    The function returns a dictionary with the following keys:
      - "expanded_query": the expanded query string,
      - "total_resume": the number of resumes required.
    """
    prompt = load_prompt("expand_query")
    response = send_openai_request(query, prompt, API_KEY)
    
    if isinstance(response, dict) and ("expanded_query" in response or "total_resume" in response):
        return response
    
    try:
        parsed_response = json.loads(response)
        return parsed_response
    except Exception:
        # Fallback: return a default dictionary if parsing fails.
        return {"expanded_query": query, "total_resume": 5}

def rerank_results(query: str, resume_ids: list) -> list:
    """
    Re-rank resume IDs based on semantic relevance using OpenAI.
    Loads a detailed prompt with placeholders that are replaced with actual values.
    """

    base_prompt = load_prompt("rerank_results")
    formatted_prompt = base_prompt.replace("{query}", query).replace("{resume_ids}", ", ".join(resume_ids))
    response = send_openai_request(query, formatted_prompt, API_KEY)
    try:
        ranked = response.get("content", resume_ids)
        if isinstance(ranked, list):
            return ranked
        else:
            return resume_ids
    except Exception:
        return resume_ids

def generate_summary(resume_text: str, query: str) -> str:
    """
    Generate a concise AI summary for a resume based on the recruiter query using OpenAI.
    The function appends the recruiter query to the candidate's resume text and sends the combined
    content along with the prompt to OpenAI. It then extracts and returns the summary.
    """
    prompt = load_prompt("generate_summary")
    # Combine the resume text with the recruiter query for context.
    combined_content = f"Resume:\n{resume_text}\n\nRecruiter Query:\n{query}"
    response = send_openai_request(combined_content, prompt, API_KEY)
    
    # If the response contains 'ranked_candidates', extract the summary from the first candidate.
    if isinstance(response, dict) and "ranked_candidates" in response:
        ranked_list = response["ranked_candidates"]
        if ranked_list and isinstance(ranked_list, list):
            return ranked_list[0].get("summary", "No summary available.")
    
    # Fallback to using the 'content' field if available.
    return response.get("content", "No summary available.")