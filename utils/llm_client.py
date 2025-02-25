import json
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

def send_openai_request(content, prompt, api_key, file_type="text"):
    """
    Sends a request to the OpenAI ChatCompletion API and returns the parsed response.
    """
    try:
        logging.info(f"Sending request to OpenAI for file_type: {file_type}")
        client = OpenAI(api_key=api_key)
        # Debug output
        if file_type == "pdf":
            messages = [
                {
                    "role": "user",
                    "content": prompt + f"\n\nHere is the PDF content from the specified pages:\n{content}"
                }
            ]
        else:
            messages = [
                {
                    "role": "user",
                    "content": prompt + f"\n\nHere is the data:\n{content}"
                }
            ]

        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4o-mini" if preferred
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
            max_completion_tokens=2048
        )

        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            gpt_content = response.choices[0].message.content
            try:
                parsed_content = json.loads(gpt_content)
                logging.info("Successfully parsed OpenAI response.")
                return parsed_content
            except json.JSONDecodeError:
                logging.warning("Failed to parse OpenAI response as JSON.")
                return {"content": gpt_content}
        else:
            logging.error("No content in OpenAI response.")
            return {"error": "No content in OpenAI response"}

    except Exception as e:
        logging.error(f"Failed to send OpenAI request: {e}")
        return {"error": str(e)}
