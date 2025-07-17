import logging
import requests
from utils import get_available_token, get_prompt

# --- DeepSeek API Configuration ---
API_URL = 'https://openrouter.ai/api/v1/chat/completions'


def summarize_text_remotely(text: str, destination_channel_link: str) -> str:
    """
    Summarize the given text using DeepSeek API, with formatting based on the period.
    """
    return process_with_deepseek(text, destination_channel_link)

def process_with_deepseek(text: str, destination_channel_link: str) -> str:
    """
    Send a summary request to DeepSeek API and return the formatted summary.
    """
    try:
        token = get_available_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        system_prompt = get_prompt()
        data = {
            "model": "deepseek/deepseek-chat:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Summarize and translate the following Arabic content into Hebrew:\n\n{text}"}
            ]
        }

        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Add the Telegram channel link at the end
            content += f"\n\nלחדשות נוספות עקבו אחר {destination_channel_link}"
            return content
        else:
            logging.error(f"Failed to fetch data from DeepSeek API. Status Code: {response.status_code}")
            return "שגיאה: לא ניתן לסכם את הטקסט כרגע."
    except Exception as e:
        logging.error(f"Token selection failed: {e}")
        return "שגיאה: כל הטוקנים חורגים מהמכסה או לא זמינים כרגע."