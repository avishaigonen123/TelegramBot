# TelegramBot
telegram bot translate and forward

simple program that use my user in telegram (this isn't a bot), 
this translate messages from a secret channel (https://t.me/SamaNewsAgency), 
and forward this into my channel :)

Here you enter to get the api data of your user.
https://my.telegram.org/auth?to=apps

you need to change the path to your python, in the run_bot.bat file.

i added vbscript files, to run the script without command window.



#פלסטיןחי


Now i also added another channel, to gada news
https://t.me/jeninnews1


how to add to my server?

```
git clone https://github.com/avishaigonen123/TelegramBot.git
 
python3 -m pip install --user googletrans==4.0.0-rc1

python3 -m pip install --user telethon
```

- set up the config file with my credentials from telegram

- in the cron job insert this line:

`bash /home/gmxceisz/TelegramBot/bot_palastine/script_bot.sh > /dev/null`
when the ***script_bot.sh*** file contains:
```
cd /home/gmxceisz/TelegramBot/bot_gada
python3 /home/gmxceisz/TelegramBot/bot_gada/bot.py
```

also, in the first time you will set it after long time, you'll need to intilize the session files.
thus, you can enter the directory, eg, bot_gada, and then run the command: `./remove_sessions.sh`

after this running `python3 create_sessions.py`, then you'll create 5 sessions, you will need to give him the secret code telegram sends you.

It might take a while... the idea is that you will use more sessions, randomly, then reduce the risk for getting blocked.
at the end, open the bot.py file and change the sessions list.
