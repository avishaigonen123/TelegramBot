import config
from googletrans import Translator
from telethon import TelegramClient
import random
import logging
import os
import glob
import pytz
from datetime import datetime

# Configure logging to use Israel Standard Time (IST)
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Custom formatter for timezone
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

# Pick random session file
sessions_list = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob("*.session")]
if not sessions_list:
    logging.error("No session files found in the current directory.")
    raise SystemExit("No session files found.")
session_name = random.choice(sessions_list)
logging.info(f"Using session file: {session_name}")

# Start Telegram client
client = TelegramClient(session_name, api_id, api_hash)


async def findGroup(GroupID: int):
    async for i in client.iter_dialogs():
        if i.id == GroupID:
            logging.info(f"Found group with ID {GroupID}: {i.name}")
            return i
    logging.warning(f"Group with ID {GroupID} not found.")
    return None


async def main():
    translator = Translator()

    source_channel = await findGroup(source_channel_id)
    destination_channel = await findGroup(destination_channel_id)

    if not source_channel or not destination_channel:
        logging.error("Could not find source or destination channel.")
        return

    logging.info(f"Fetching last 5 messages from: {source_channel.name}")
    mess = []

    try:
        async for i in client.iter_messages(source_channel, limit=5):
            if not i.action:  # skip service messages
                mess.insert(0, i)
    except Exception as e:
        logging.error(f"Error while fetching messages: {e}")
        return

    if not mess:
        logging.info("No messages fetched.")
        return

    for i in mess:
        try:
            if not i.text and not i.media:
                logging.info(f"Skipping empty message ID {i.id}")
                continue

            original_text = i.text or ""
            logging.info(f"Fetched message ID {i.id}")

            try:
                translated_text = translator.translate(original_text, dest='he').text
                logging.info(f"Translated message ID {i.id}")
            except Exception as e:
                logging.warning(f"Translation failed for message ID {i.id}: {e}")
                translated_text = f"[Translation failed] {original_text}"

            if i.media:
                try:
                    await client.send_message(destination_channel, file=i.media, message=translated_text)
                    logging.info(f"Sent media message ID {i.id} with caption")
                except Exception as e:
                    logging.warning(f"Caption too long or error sending media with caption for message ID {i.id}: {e}")
                    try:
                        await client.send_message(destination_channel, file=i.media)
                        logging.info(f"Sent media message ID {i.id} without caption")
                    except Exception as e2:
                        logging.error(f"Error sending media message ID {i.id} without caption: {e2}")
            else:
                try:
                    await client.send_message(destination_channel, translated_text)
                    logging.info(f"Sent text message ID {i.id}")
                except Exception as e:
                    logging.error(f"Error sending text message ID {i.id}: {e}")

            # Acknowledge as read
            await client.send_read_acknowledge(source_channel, max_id=i.id)
            logging.info(f"Acknowledged message ID {i.id}")

        except Exception as e:
            logging.error(f"Error processing message ID {i.id}: {e}")


client.start(phone_number)
client.loop.run_until_complete(main())
