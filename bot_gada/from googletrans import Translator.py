from googletrans import Translator
from telethon import TelegramClient, events, types
import random

# Replace '22426045' and 'e7b8ee99e8bf9c36984d18f1baae5591' with your actual API ID and API hash
api_id = 22426045
api_hash = 'e7b8ee99e8bf9c36984d18f1baae5591'

# Replace 'mySession' with a unique session name
session_name = 'gonenSession'
sessions_list = ['gonenSession934705', 'gonenSession557142', 'gonenSession789754', 'gonenSession562588', 'gonenSession530415']

# Replace '-1001300814792' with the actual chat ID of the source channel
source_channel_id = -1001236978606

# Replace '-1002027365084' with the actual chat ID of your bot's channel
destination_channel_id = -1002046754990

# Create a TelegramClient instance
client = TelegramClient(sessions_list[random.randint(0,len(sessions_list)-1)], api_id, api_hash) 

        
async def findGroup(GroupID: int):
    async for i in client.iter_dialogs(folder=0):
        if i.id==GroupID:
            return i

async def main():
    translator = Translator()
    dialogs = await client.get_dialogs()
    for dia in dialogs:
      if dia.name == 'جنين القسام تقـــاوم 🔥✊':
          print(dia)
    
client.start("+972585328077")
# Run the main function once before starting the event loop
client.loop.run_until_complete(main()) # i want that first it will send all the unread messages, and then it will use the event mechanic.

