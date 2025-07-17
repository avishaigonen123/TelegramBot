import logging
import pytz
import requests
from datetime import datetime
from config import OPEN_ROUTER_TOKEN

# --- DeepSeek API Configuration ---
API_KEY = OPEN_ROUTER_TOKEN
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# --- Request Headers ---
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def summarize_text_remotely(text: str, destination_channel_link: str) -> str:
    """
    Summarize the given text using DeepSeek API, with formatting based on the period.
    """
    return process_with_deepseek(text, destination_channel_link)

def process_with_deepseek(text: str, destination_channel_link: str) -> str:
    """
    Send a summary request to DeepSeek API and return the formatted summary.
    """
    now = datetime.now(pytz.timezone('Asia/Jerusalem'))
    hour_str = now.strftime("%H:%M")
    hour = now.hour

    if hour < 12:
        period_title = f"🌞 חדשות הבוקר (נכון לשעה {hour_str}):"
    elif 12 <= hour < 18:
        period_title = f"🌤️ חדשות הצהריים (נכון לשעה {hour_str}):"
    else:
        period_title = f"🌙 חדשות הלילה (נכון לשעה {hour_str}):"

    # --- System Prompt ---
    system_prompt = (
        f"You are a multilingual assistant. Summarize a list of Arabic news items into a **single**, well-structured Hebrew message to be posted on Telegram.\n\n"
        f"Start the message with this title on its own line:\n"
        f"{period_title}\n\n"
        f"Then leave a blank line and write **exactly 10** bullet points. Each bullet should:\n"
        f"- Start with a strong action word or event (e.g., פיצוץ, מעצר, תקיפה)\n"
        f"- Be no more than 2 short lines (avoid paragraphs)\n"
        f"- Include a relevant emoji\n"
        f"- Use double asterisks (**) to bold important names/terms\n"
        f"- Be readable, punchy, and clear\n\n"
        f"End the message with one final line: an emotional, human touch (e.g., wish for peace).\n\n"
        f"Don't use hashtags, markdown headers, or intro text before the bullets.\n"
        f"Make the message feel emotional, fun to read, yet informative."
    )

    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Summarize and translate the following Arabic content into Hebrew:\n\n{text}"}
        ]
    }

    try:
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
        logging.error(f"שגיאה במהלך שליחת הבקשה ל-DeepSeek: {e}")
        return "שגיאה: לא ניתן לסכם את הטקסט כרגע."
