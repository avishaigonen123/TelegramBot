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
 
python3 -m pip install --user googletrans

python3 -m pip install --user telethon
```

- set up the config file with my credentials from telegram

- in the cron job insert this line:

`python3 /home/gmxceisz/TelegramBot/bot_zaken/DOS_zaken.py > /dev/null`
