from googletrans import Translator
from telethon import TelegramClient, events, types
from datetime import datetime, timedelta


# Replace '22426045' and 'e7b8ee99e8bf9c36984d18f1baae5591' with your actual API ID and API hash
api_id = 22426045
api_hash = 'e7b8ee99e8bf9c36984d18f1baae5591'

# Replace 'mySession' with a unique session name
session_name = 'gonenSession493804.session'

# Replace '-1001300814792' with the actual chat ID of the source channel
source_channel_id = -1001300814792

# Replace '-1002027365084' with the actual chat ID of your bot's channel
user_id = 1146451596

# Create a TelegramClient instance
client = TelegramClient(session_name, api_id, api_hash)

def findGroup(GroupID: int):
     for i in client.iter_dialogs(folder=0):
        if i.id==GroupID:
            return i
        


async def send_message_to_user():
    # Connect to Telegram
    await client.start('+972585328077')

    # Get the current date and time
    now = datetime.now()

    # Add 2 hours to the current time
    new_time = now + timedelta(hours=3)
    
     # Format the current time as HH:MM
    current_time = new_time.strftime("%H:%M")
    await client.send_message(user_id, "hello, it's: "+current_time+" now")

    await client.disconnect()

# Run the send_message_to_user function
client.loop.run_until_complete(send_message_to_user())
