from datetime import datetime, timedelta, time
import logging
import pytz
import os
import glob
import random
from telethon import TelegramClient

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

def get_time_range(period):
    """
    Get start and end datetime objects for the requested period ("day" or "night").
    "day": 8AM to 8PM today
    "night": 8PM yesterday to 8AM today
    """
    tz = pytz.timezone('Asia/Jerusalem')
    now = datetime.now(tz)
    if period == "day":
        start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end = now.replace(hour=20, minute=0, second=0, microsecond=0)
    elif period == "night":
        start = (now - timedelta(days=1)).replace(hour=20, minute=0, second=0, microsecond=0)
        end = now.replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        raise ValueError("period must be 'day' or 'night'")
    return start, end

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
