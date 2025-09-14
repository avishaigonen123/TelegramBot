# Telegram Bot Restore Guide 

This document explains how to quickly restore your Telegram Bot from backup when setting up a fresh VPS. 

--- 

## 🔄 Restore Steps 

1. **Download the latest backup archive**
```bash
   wget https://e5e01cfdc4cd.ngrok-free.app/TelegramBot_backup_2025-07-17.zip
```

2. **Extract the archive**
```bash
    unzip TelegramBot_backup_2025-07-17.zip
    cd TelegramBot
```

3. **Replace placeholder username with your system username**
```bash
    find . -type f -exec sed -i "s/xdfqunme/$(whoami)/g" {} +
```
> This makes sure paths and permissions match your current VPS user.

4. **Install Python dependencies**
```bash
    python3 -m pip install -r requirements.txt --user
```

5. **Update last message IDs**
```bash
    ./scripts/update_all_last_id.sh
```
> This step ensures the bot doesn’t resend old messages.

6. **Restore cron jobs**
```bash
    crontab crontab_backup.txt
```
> Verify cron jobs with:
`crontab -l`

--- 

### 🍀 Good Luck!

Welcome back online — may your bot run smoothly and never get deleted again 🙌