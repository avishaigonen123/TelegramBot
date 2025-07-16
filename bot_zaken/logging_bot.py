import config
from googletrans import Translator
from telethon import TelegramClient, events, types
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

api_id = config.API_ID
api_hash = config.API_HASH

source_channel_id = config.SOURCE_CHANNEL_ID
destination_channel_id = config.DEST_CHANNEL_ID

phone_number = config.PHONE_NUMBER

sessions_list = ['gonenSession61396', 'gonenSession407480', 'gonenSession165136', 'gonenSession178987', 'gonenSession179476']

# Create a TelegramClient instance
client = TelegramClient(sessions_list[random.randint(0, len(sessions_list) - 1)], api_id, api_hash)


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
                if not (i.action):  # patched.Message.
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
                        try:
                            await client.send_message(destination_channel, sendMes)
                        except Exception as e:
                            if 'caption is too long' in str(e):
                                if sendMes.media and sendMes.text:
                                    short_text = sendMes.text[:1000] + '... [truncated]'
                                    await client.send_message(destination_channel, file=sendMes.media, caption=short_text)
                                    logging.warning(f"Caption too long for message ID {i.id}, sent truncated version.")
                                else:
                                    logging.error(f"Unhandled caption too long error for message ID {i.id}: {e}")
                            else:
                                raise

                    await client.send_read_acknowledge(source_channel, max_id=i.id)
                    logging.info(f"Sent and acknowledged message ID {i.id}")
                except Exception as e:
                    logging.error(f"Error sending/acknowledging message ID {i.id}: {e}")


client.start(phone_number)
client.loop.run_until_complete(main())
