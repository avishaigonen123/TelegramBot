# Deploying the consolidated bot to webhostmost

## 1. Upload the new files
Via the DirectAdmin File Manager (or FTP), replace the contents of `/home/xdfqunme/TelegramBot/` with this repo's contents. The old `bots/`, `scripts_for_auto_running_windows/`, and `logs/` directories have been removed locally — delete them on the server too.

## 2. Install dependencies
If the host offers a "Setup Python App" tool in the panel, point it at this directory and install from `requirements.txt`. Otherwise, if there's any shell access via the panel:
```
pip3 install --user -r requirements.txt
```

## 3. Place secrets
Create `.env` on the server (never commit this file — it's gitignored):
```
API_ID=22426045
API_HASH=<the real value>
PHONE_NUMBER=+972585328077
OPENROUTER_API_KEYS=<comma-separated keys>
HEALTHCHECK_URL=<optional healthchecks.io ping URL>
WEBHOSTMOST_EMAIL=<client.webhostmost.com login>
WEBHOSTMOST_PASSWORD=<client.webhostmost.com password>
```

## 4. Place the session
Upload `session/main.session` (already-authorized, reused from the old `bot_jenin/gonenSession165136.session`). If it's ever invalidated, run `python3 create_session.py` interactively to mint a new one — you'll get a login code in the Telegram app.

## 5. Update the crontab
Replace the existing crontab with `crontab.txt`'s contents (via the panel's cron UI, or `crontab crontab.txt` if shell access exists).

## 6. GitHub Actions secrets (webhostmost keep-alive)
In the `avishaigonen123/TelegramBot` repo settings → Secrets and variables → Actions, add:
- `WEBHOSTMOST_EMAIL`
- `WEBHOSTMOST_PASSWORD`

The `.github/workflows/keep_alive.yml` workflow runs daily and resets the suspension timer — no changes needed on the server itself for this part.

## 7. Verify
Watch `bot.log` on the server for a few cron ticks and confirm messages are being translated and forwarded. `state/last_ids.json` should update per channel. If `HEALTHCHECK_URL` is set, confirm a ping shows up in the healthchecks.io dashboard after each tick.
