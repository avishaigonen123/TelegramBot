from datetime import datetime, timedelta, time
import logging
import pytz
import os
import glob
import random
import requests
from telethon import TelegramClient
from telethon.tl.functions.messages import ExportChatInviteRequest
from config import OPEN_ROUTER_TOKENS

logging.basicConfig(level=logging.INFO)

# --- Telegram Client Utilities ---

def connect_to_client(api_id, api_hash):
    """
    Connect to Telegram using a random session file from the current directory.
    """
    sessions_list = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob("*.session")]
    if not sessions_list:
        logging.error("No session files found in the current directory.")
        raise SystemExit("No session files found.")
    session_name = random.choice(sessions_list)
    logging.info(f"Using session file: {session_name}")
    return TelegramClient(session_name, api_id, api_hash)

async def find_group(client: TelegramClient, GroupID: int):
    """
    Find a Telegram group/channel by its ID.
    """
    async for i in client.iter_dialogs():
        if i.id == GroupID:
            logging.info(f"Found group with ID {GroupID}: {i.name}")
            return i
    logging.warning(f"Group with ID {GroupID} not found.")
    return None

async def fetch_messages(client, source_channel, num_messages=100):
    """
    Fetch the latest messages from a Telegram channel/group.
    """
    messages = []
    try:        
        logging.info(f"Fetching {num_messages} messages from: {source_channel.name}")
        async for i in client.iter_messages(source_channel, limit=num_messages):
            if not i.action:  # skip service messages
                messages.insert(0, i)  # ensure chronological order
    except Exception as e:
        logging.error(f"Error while fetching messages: {e}")
        return []
    return messages

async def send_message(client, summary, destination_channel):
    """
    Send a summary message to the destination channel/group.
    """
    logging.info(f"Sending summary to {destination_channel.name}...")
    await client.send_message(destination_channel, summary)
    logging.info("✅ Summary sent successfully.")

# --- Message Filtering Utilities ---

def get_last_12_hours_range():
    """
    Returns the datetime range for the last 12 hours in Asia/Jerusalem timezone.
    """
    tz = pytz.timezone('Asia/Jerusalem')
    now = datetime.now(tz)
    start = now - timedelta(hours=12)
    return start, now

def filter_messages(collected_messages, start_dt, end_dt):
    """
    Filter messages by a datetime range (inclusive start, exclusive end).
    Returns a list of dicts with id, time, and content.
    """
    filtered = []
    for i in collected_messages:
        try:
            if not i.text and not i.media:
                logging.info(f"Skipping empty message ID {i.id}")
                continue

            msg_datetime = i.date.astimezone(pytz.timezone('Asia/Jerusalem'))
            if not (start_dt <= msg_datetime < end_dt):
                logging.info(f"Skipping message ID {i.id} outside time range: {msg_datetime}")
                continue

            content = i.text or ""
            filtered.append({
                "id": i.id,
                "time": msg_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "content": content
            })
            logging.info(f"Collected message ID {i.id} at {msg_datetime}")

        except Exception as e:
            logging.error(f"Error processing message ID {i.id}: {e}")

    return filtered

async def get_channel_link(client, channel_id):
    try:
        # Get the channel entity
        channel = await client.get_entity(channel_id)
        
        # Export the invite link for the private channel
        invite_link = await client(ExportChatInviteRequest(channel))

        return invite_link.link
    except Exception as e:
        print(f"Error: {e}")

# --- deepseek API Utilities ---

def get_available_token() -> str:
    """
    Tries each token with a dry-run to find one that is not rate-limited.
    Returns the first usable token or raises an Exception.
    """
    api_url = 'https://openrouter.ai/api/v1/chat/completions'
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {"role": "user", "content": "Hello, who are you?"}
        ]
    }

    for token in OPEN_ROUTER_TOKENS:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Shallow check: make a HEAD or minimal POST request
        try:
            test_data = data.copy()
            test_data["messages"][-1]["content"] = "ping"
            response = requests.post(api_url, json=test_data, headers=headers)

            if response.status_code == 200:
                logging.info(f"Using available token: {token[:5]}...")  # Log partial token for debug
                return token
            elif response.status_code == 429:
                logging.warning(f"Token rate-limited: {token[:5]}..., trying next.")
                continue
            else:
                logging.error(f"Unexpected response with token {token[:5]}...: {response.status_code}")
        except Exception as e:
            logging.error(f"Exception while testing token {token[:5]}...: {e}")
            continue

    raise Exception("❌ All tokens are rate-limited or invalid.")

def get_prompt() -> str:
    '''
    Generate the system prompt for summarization.
    This includes the period title based on the current time.
    '''
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

    return system_prompt