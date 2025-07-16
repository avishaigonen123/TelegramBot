import config
from googletrans import Translator
from telethon import TelegramClient
import random
import logging
import os
import glob
import pytz
from datetime import datetime

# Timezone-aware logging (Israel Standard Time)
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = lambda *args, **kwargs: datetime.now(pytz.timezone('Asia/Jerusalem')).timetuple()
for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

# Load config
api_id = config.API_ID
api_hash = config.API_HASH
source_channel_id = config.SOURCE_CHANNEL_ID
destination_channel_id = config.DEST_CHANNEL_ID
phone_number = config.PHONE_NUMBER

# Session file picker
sessions_list = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob("*.session")]
if not sessions_list:
    logging.error("No session files found in the current directory.")
    raise SystemExit("No session files found.")
session_name = random.choice(sessions_list)
logging.info(f"Using session file: {session_name}")

# Telegram client
client = TelegramClient(session_name, api_id, api_hash)

# File to store last processed message ID
LAST_ID_FILE = "last_id.txt"

def get_last_processed_id():
    try:
        if os.path.exists(LAST_ID_FILE):
            with open(LAST_ID_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return int(content)
    except Exception as e:
        logging.error(f"Error reading last processed ID from file: {e}")
    return None

def save_last_processed_id(msg_id):
    try:
        with open(LAST_ID_FILE, "w") as f:
            f.write(str(msg_id))
    except Exception as e:
        logging.error(f"Error saving last processed ID to file: {e}")

async def findGroup(GroupID: int):
    async for i in client.iter_dialogs():
        if i.id == GroupID:
            logging.info(f"Found group with ID {GroupID}: {i.name}")
            return i
    logging.warning(f"Group with ID {GroupID} not found.")
    return None

async def main():
    translator = Translator()
    last_id = get_last_processed_id()

    source_channel = await findGroup(source_channel_id)
    destination_channel = await findGroup(destination_channel_id)

    if not source_channel or not destination_channel:
        logging.error("Could not find source or destination channel.")
        return

    messages = []

    try:
        if last_id is None:
            logging.info("No last processed ID found, fetching last 10 messages.")
            async for msg in client.iter_messages(source_channel, limit=10, reverse=True):
                if not msg.action:
                    messages.append(msg)
        else:
            logging.info(f"Fetching messages after message ID {last_id}")
            async for msg in client.iter_messages(source_channel, min_id=last_id, reverse=True):
                if not msg.action:
                    messages.append(msg)
    except Exception as e:
        logging.error(f"Error while fetching messages: {e}")
        return

    if not messages:
        logging.info("No new messages to process.")
        return

    for msg in messages:
        try:
            if not msg.text and not msg.media:
                logging.info(f"Skipping empty message ID {msg.id}")
                continue

            original_text = msg.text or ""
            translated_text = ""

            if original_text.strip():
                try:
                    translated_text = translator.translate(original_text, dest='he').text
                    logging.info(f"Translated message ID {msg.id}")
                except Exception as e:
                    logging.warning(f"Translation failed for message ID {msg.id}: {e}")

            # Handle media
            if msg.media:
                try:
                    await client.send_message(destination_channel, file=msg.media, message=translated_text)
                    logging.info(f"Sent media message ID {msg.id} with caption")
                except Exception as e:
                    logging.warning(f"Failed with caption, trying without caption: {e}")
                    try:
                        await client.send_message(destination_channel, file=msg.media)
                        logging.info(f"Sent media message ID {msg.id} without caption")
                    except Exception as e2:
                        logging.error(f"Failed sending media message ID {msg.id}: {e2}")
            else:
                try:
                    await client.send_message(destination_channel, translated_text)
                    logging.info(f"Sent text message ID {msg.id}")
                except Exception as e:
                    logging.error(f"Error sending text message ID {msg.id}: {e}")

            # Mark as read
            await client.send_read_acknowledge(source_channel, max_id=msg.id)
            logging.info(f"Acknowledged message ID {msg.id}")

            # Save the last processed message ID
            save_last_processed_id(msg.id)

        except Exception as e:
            logging.error(f"Error processing message ID {msg.id}: {e}")

# Run
client.start(phone_number)
client.loop.run_until_complete(main())