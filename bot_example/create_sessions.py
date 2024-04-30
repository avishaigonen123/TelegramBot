from telethon import TelegramClient, events, types
import random

# Replace '22426045' and 'e7b8ee99e8bf9c36984d18f1baae5591' with your actual API ID and API hash
api_id = 22426045
api_hash = 'e7b8ee99e8bf9c36984d18f1baae5591'

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

