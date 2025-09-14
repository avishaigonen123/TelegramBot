from flask import Flask
import subprocess
from googletrans import Translator
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession

from datetime import datetime, timedelta
import os
import asyncio

app = Flask(__name__)

# Load environment variables
api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
user_id = int(os.environ["USER_ID"])
string_session = os.environ["STRING_SESSION"]

# Create Telegram client
client = TelegramClient(StringSession(string_session), api_id, api_hash)

async def send_message_to_user():
    await client.start()
    # Optional: calculate time
    now = datetime.now()
    new_time = now + timedelta(hours=2)
    current_time = new_time.strftime("%H:%M")

    await client.send_message('me', f"✅ Hello! It's {current_time} now.")
    return "✅ Message sent"

@app.route('/')
def index():
    return asyncio.run(send_message_to_user())



