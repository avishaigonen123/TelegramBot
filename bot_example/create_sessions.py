import config
from telethon import TelegramClient, events, types
import random

api_id = config.API_ID
api_hash = config.API_HASH

# Replace 'mySession' with a unique session name

sessions_names = []

for i in range(5):
    session_name = 'gonenSession'+str(random.randint(10,1000000))
    print(session_name)

    client = TelegramClient(session_name, api_id, api_hash)

    client.start("+972585328077")
    
    sessions_names.append(session_name)

print("sessions created: ")
print(sessions_names)

