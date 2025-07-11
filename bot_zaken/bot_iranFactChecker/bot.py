import config
from googletrans import Translator
from telethon import TelegramClient, events, types
import random
import logging
import os
import glob
import pytz
from datetime import datetime

# Configure logging to use Israel Standard Time (IST)
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a custom formatter to adjust for the Israel timezone
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = lambda *args, **kwargs: datetime.now(pytz.timezone('Asia/Jerusalem')).timetuple()

# Apply the custom formatter to the root logger
for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)


api_id = config.API_ID
api_hash = config.API_HASH

source_channel_id = config.SOURCE_CHANNEL_ID
destination_channel_id = config.DEST_CHANNEL_ID

phone_number = config.PHONE_NUMBER

# Find all .session files in the current directory
sessions_list = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob("*.session")]

if not sessions_list:
    logging.error("No session files found in the current directory.")
    raise SystemExit("No session files found.")

# Pick a random session
session_name = random.choice(sessions_list)
logging.info(f"Using session file: {session_name}")

# Create a TelegramClient instance
client = TelegramClient(session_name, api_id, api_hash)


async def findGroup(GroupID: int):
    async for i in client.iter_dialogs(folder=0):
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

    if source_channel.unread_count != 0:
        count = source_channel.unread_count
        mess = []
        logging.info(f"Found {count} unread messages in source channel.")

        try:
            async for i in client.iter_messages(source_channel, limit=count):
                if not i.action:  # skip service messages like "pinned", "user joined", etc.
                    mess.insert(0, i)
        except Exception as e:
            logging.error(f"Error while fetching messages: {e}")
            return

        if len(mess) > 0:
            for i in mess:
                try:
                    sendMes = i
                    if sendMes.text:
                        try:
                            original_text = sendMes.text
                            translated_text = translator.translate(original_text, dest='he').text
                            sendMes.text = translated_text
                            logging.info(f"Translated message ID {i.id}")
                        except Exception as e:
                            logging.warning(f"Error: Translation failed for message ID {i.id}: {e}")
                            sendMes.text = f"[Translation failed] {sendMes.text}"

                        # Handle media and text separately
                        if sendMes.media:
                            try:
                                await client.send_message(destination_channel, file=sendMes.media, caption=sendMes.text)
                                logging.info(f"Sent media message ID {i.id} with caption")
                            except Exception as e:
                                logging.error(f"Error sending media message ID {i.id}: {e}")
                        else:
                            try:
                                await client.send_message(destination_channel, text=sendMes.text)
                                logging.info(f"Sent text message ID {i.id}")
                            except Exception as e:
                                logging.error(f"Error sending text message ID {i.id}: {e}")

                    await client.send_read_acknowledge(source_channel, max_id=i.id)
                    logging.info(f"Sent and acknowledged message ID {i.id}")
                except Exception as e:
                    logging.error(f"Error sending/acknowledging message ID {i.id}: {e}")


client.start(phone_number)
client.loop.run_until_complete(main())
