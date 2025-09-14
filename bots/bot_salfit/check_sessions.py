import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, AuthKeyUnregisteredError
import asyncio
import config  # Importing from config.py

# Use values from config.py
api_id = config.API_ID
api_hash = config.API_HASH
phone_number = config.PHONE_NUMBER

SESSIONS_FOLDER = './'  # Root folder (current directory)

# Function to search recursively for all .session files
def find_session_files(directory):
    session_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.session'):
                session_files.append(os.path.join(root, file))
    return session_files

async def check_session(session_path):
    session_name = os.path.splitext(os.path.basename(session_path))[0]
    
    # Correct initialization without the 'session' argument
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[❌] {session_name} is not authorized.")
        else:
            me = await client.get_me()
            print(f"[✅] {session_name} is ACTIVE: @{me.username or me.first_name}")
    except AuthKeyUnregisteredError:
        print(f"[❌] {session_name} has no valid auth key.")
    except SessionPasswordNeededError:
        print(f"[❌] {session_name} needs a password.")
    except Exception as e:
        print(f"[⚠️] {session_name} error: {e}")
    finally:
        await client.disconnect()

async def main():
    # Find all session files recursively
    session_files = find_session_files(SESSIONS_FOLDER)
    tasks = []

    for file in session_files:
        tasks.append(check_session(file))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Manually create and run the event loop for older Python versions
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
