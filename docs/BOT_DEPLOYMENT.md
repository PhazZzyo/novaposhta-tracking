# Nova Poshta Telegram Bot - Deployment Guide

## Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Python 3.12+
- Virtual environment set up
- `.env` file with `TELEGRAM_BOT_TOKEN`
- Flask app already running (bot imports from app.py)

---

## 1. Test Bot Manually First

Before setting up the service, test that the bot works:

```bash
cd /home/sysadmin/np
source venv/bin/activate
python telegram_bot.py
```

Send `/start` to @Orthotrack_bot in Telegram.
If it responds, press `Ctrl+C` and proceed.

---

## 2. Create systemd Service

```bash
sudo nano /etc/systemd/system/novaposhta-bot.service
```

Paste this content:

```ini
[Unit]
Description=Nova Poshta Telegram Bot
After=network.target novaposhta.service
Wants=network-online.target

[Service]
User=sysadmin
Group=sysadmin
WorkingDirectory=/home/sysadmin/np
Environment="PATH=/home/sysadmin/np/venv/bin"
EnvironmentFile=/home/sysadmin/np/.env
ExecStart=/home/sysadmin/np/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

> **Note:** `After=novaposhta.service` ensures the bot starts after the Flask app,
> since the bot imports models from `app.py`.

---

## 3. Enable and Start Service

```bash
# Reload systemd to pick up new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable novaposhta-bot

# Start service now
sudo systemctl start novaposhta-bot

# Check status
sudo systemctl status novaposhta-bot
```

Expected output:
```
● novaposhta-bot.service - Nova Poshta Telegram Bot
     Loaded: loaded (/etc/systemd/system/novaposhta-bot.service; enabled)
     Active: active (running)
```

---

## 4. Verify It's Working

```bash
# View live logs
sudo journalctl -u novaposhta-bot -f
```

Send `/start` to @Orthotrack_bot - you should see log entries appear.

---

## Management Commands

```bash
# Start
sudo systemctl start novaposhta-bot

# Stop
sudo systemctl stop novaposhta-bot

# Restart (after code changes)
sudo systemctl restart novaposhta-bot

# View live logs
sudo journalctl -u novaposhta-bot -f

# View last 100 lines of logs
sudo journalctl -u novaposhta-bot -n 100
```

---

## Updating the Bot

```bash
# Pull latest code
cd /home/sysadmin/np
git pull

# Restart bot service
sudo systemctl restart novaposhta-bot

# Verify it's running
sudo systemctl status novaposhta-bot
```

---

## Troubleshooting

### Bot not responding
```bash
# Check service status
sudo systemctl status novaposhta-bot

# Check logs for errors
sudo journalctl -u novaposhta-bot -n 50 --no-pager
```

### Token not found error
```bash
# Check .env file has the token
cat /home/sysadmin/np/.env | grep TELEGRAM

# Should show:
# TELEGRAM_BOT_TOKEN=your_token_here
```

### Bot starts but crashes immediately
```bash
# Test manually to see full error
cd /home/sysadmin/np
source venv/bin/activate
python telegram_bot.py
```

### Timeout errors (WSL2 only)
This is a WSL2 network issue. On a real Linux server this should not happen.
If it does, the bot will retry automatically due to `Restart=always`.

### Import errors (can't import from app.py)
```bash
# Make sure Flask app dependencies are installed
cd /home/sysadmin/np
source venv/bin/activate
pip install -r requirements.txt

# Test import manually
python -c "from app import app, db, User, Package"
```

### Bot running twice (conflict)
```bash
# Check if bot is already running
ps aux | grep telegram_bot

# Kill any manual instances
pkill -f telegram_bot.py

# Then restart service
sudo systemctl restart novaposhta-bot
```

---

## Both Services - Start Order

The correct start order is:

```
1. novaposhta.service     (Flask app)
2. novaposhta-bot.service (Telegram bot)
```

This is handled automatically by `After=novaposhta.service` in the bot service file.

To start both at once:

```bash
sudo systemctl start novaposhta novaposhta-bot
```

To restart both at once:

```bash
sudo systemctl restart novaposhta novaposhta-bot
```

To check status of both:

```bash
sudo systemctl status novaposhta novaposhta-bot
```

---

## Verify Both Running After Reboot

```bash
# Reboot server
sudo reboot

# After reboot, check both services
sudo systemctl status novaposhta
sudo systemctl status novaposhta-bot
```

---

## Production Checklist

- [ ] `TELEGRAM_BOT_TOKEN` set in `.env`
- [ ] Bot tested manually before service setup
- [ ] Service file created and enabled
- [ ] Both services start on boot
- [ ] Tested after reboot
- [ ] No manual bot instances running
- [ ] Logs accessible via journalctl
