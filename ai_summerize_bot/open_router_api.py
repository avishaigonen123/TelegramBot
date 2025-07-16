import logging
import requests
from config import OPEN_ROUTER_TOKEN

# --- DeepSeek API Configuration ---
API_KEY = OPEN_ROUTER_TOKEN
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# --- Request Headers ---
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def summarize_text_remotely(text: str, period: str) -> str:
    """
    Summarize the given text using DeepSeek API, with formatting based on the period.
    """
    return process_with_deepseek(text, period)

def process_with_deepseek(text: str, period: str) -> str:
    """
    Send a summary request to DeepSeek API and return the formatted summary.
    """
    period_title = "🌞 חדשות היום" if period == "day" else "🌙 חדשות הלילה"

    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a multilingual assistant. Summarize a list of Arabic news items into a **single**, well-structured Hebrew message. "
                    f"Add an engaging and funny tone with emojis and **bolded key terms** (use `**bold**`, not markdown headers). "
                    f"Start the message with the phrase '{period_title}' followed by a colon. Then write the summary as bullet points. "
                    f"This will be posted in a Telegram channel, so make it feel like a short and fun news digest, but still clear and informative. "
                    f"Keep it concise. No hashtags. No long intros. No headlines with ### or ===."
                )
            },
            {
                "role": "user",
                "content": f"Summarize and translate the following Arabic content into Hebrew:\n\n{text}"
            }
        ]
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            return content
        else:
            logging.error(f"Failed to fetch data from DeepSeek API. Status Code: {response.status_code}")
            return "Error: Unable to summarize text."
    except Exception as e:
        logging.error(f"Exception during DeepSeek API request: {e}")
        return "Error: Unable to summarize text."