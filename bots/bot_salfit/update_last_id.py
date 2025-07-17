from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
import asyncio
from config import API_ID, API_HASH, SOURCE_CHANNEL_ID, DEST_CHANNEL_ID, PHONE_NUMBER
import logging
import os
import random
import glob

logging.basicConfig(level=logging.INFO)

# Load config
api_id = API_ID
api_hash = API_HASH
source_channel_id = SOURCE_CHANNEL_ID
destination_channel_id = DEST_CHANNEL_ID
phone_number =  PHONE_NUMBER

# Session file picker
sessions_list = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob("*.session")]
if not sessions_list:
    logging.error("No session files found in the current directory.")
    raise SystemExit("No session files found.")
session_name = random.choice(sessions_list)
logging.info(f"Using session file: {session_name}")

# Telegram client
client = TelegramClient(session_name, api_id, api_hash)
last_id_file = "last_id.txt"

async def main():
    try:
        entity = await client.get_entity(PeerChannel(source_channel_id))
    except Exception as e:
        logging.error(f"Failed to fetch channel: {e}")
        return

    # Get the latest message
    messages = await client.get_messages(entity, limit=1)
    if not messages:
        print("No messages found in channel.")
        return

    last_message_id = messages[0].id
    print(f"Latest message ID: {last_message_id}")

    # Save to file
    with open(last_id_file, 'w') as f:
        f.write(str(last_message_id))
    print(f"Saved last ID to {last_id_file}")

# Run
client.start(phone_number)
client.loop.run_until_complete(main())
