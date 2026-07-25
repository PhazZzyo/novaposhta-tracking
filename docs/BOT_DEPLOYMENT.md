# Nova Poshta Telegram Bot & Scheduler - Deployment Guide

## Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Python 3.12+
- Virtual environment set up
- `.env` file with `TELEGRAM_BOT_TOKEN`
- Flask app already running (bot and scheduler import from app.py)

---

## Architecture

The app runs as **three separate systemd services**:

```
novaposhta.service            → Web app (Gunicorn, multiple workers)
novaposhta-bot.service        → Telegram bot (single process, polling)
novaposhta-scheduler.service  → Auto-sync scheduler (single process)
```

> **Why separate processes?** Gunicorn runs multiple worker processes for the
> web app. If the scheduler ran inside a web worker, every worker would start
> its own scheduler instance, causing duplicate syncs and race conditions
> (e.g. `UNIQUE constraint failed: packages.tracking_number`). Running the
> bot and scheduler as their own single-instance services avoids this.

---

## 1. Test Bot Manually First

```bash
cd /home/user/novaposhta-tracking
source venv/bin/activate
python telegram_bot.py
```

Send `/start` to @your_bot in Telegram.
If it responds, press `Ctrl+C` and proceed.

---

## 2. Test Scheduler Manually First

```bash
cd /home/user/novaposhta-tracking
source venv/bin/activate
python scheduler_service.py
```

Expected output:
```
✅ Scheduler service started - syncing every 30min (8:00-20:00 Kyiv time)
Running initial sync on startup...
Auto-synced: <API key label> - <result>
```

Press `Ctrl+C` to stop after confirming it works.

---

## 3. Install/Update Services Automatically

Instead of creating systemd unit files by hand, use `install_services.sh`.
It is **idempotent** — safe to run every deploy, only creates/updates a
service file if it doesn't exist or its content changed.

```bash
cd /home/user/novaposhta-tracking
chmod +x install_services.sh
bash install_services.sh
```

This creates/updates all three services:
- `novaposhta.service`
- `novaposhta-bot.service`
- `novaposhta-scheduler.service`

And enables them to start on boot automatically.

---

## 4. Start Services

```bash
sudo systemctl start novaposhta novaposhta-bot novaposhta-scheduler
```

Check status:
```bash
sudo systemctl status novaposhta novaposhta-bot novaposhta-scheduler
```

Expected output for each:
```
● novaposhta-bot.service - Nova Poshta Telegram Bot
     Active: active (running)

● novaposhta-scheduler.service - Nova Poshta Auto-Sync Scheduler
     Active: active (running)
```

---

## 5. Verify It's Working

### Bot:
```bash
sudo journalctl -u novaposhta-bot -f
```
Send `/start` to @your_bot - you should see log entries appear.

### Scheduler:
```bash
sudo journalctl -u novaposhta-scheduler -f
```
On startup it runs an immediate sync, then every 30 minutes between
8:00-20:00 Kyiv time. You should see:
```
Auto-synced: <label> - No updates
Auto-synced: <label> - In: 3📦 (1🆕)
```

### Notifications end-to-end:
When the scheduler detects a status change (package arrives at branch,
status codes `7`/`8`, or delivered `9`) on an **incoming** package, it
calls `notify_package_status_change()` which sends a Telegram message to
all admins and users tracking that API key who have linked their Telegram
account and enabled notifications.

---

## Management Commands

```bash
# Start all
sudo systemctl start novaposhta novaposhta-bot novaposhta-scheduler

# Stop all
sudo systemctl stop novaposhta novaposhta-bot novaposhta-scheduler

# Restart all (after code changes)
sudo systemctl restart novaposhta novaposhta-bot novaposhta-scheduler

# View live logs
sudo journalctl -u novaposhta-bot -f
sudo journalctl -u novaposhta-scheduler -f

# View last 100 lines
sudo journalctl -u novaposhta-bot -n 100
sudo journalctl -u novaposhta-scheduler -n 100
```

---

## Updating

Use the deploy script - it pulls code, installs dependencies, runs
migrations, updates services (via `install_services.sh`), and restarts
everything:

```bash
cd /home/user/novaposhta-tracking
./deploy.sh
```

---

## Troubleshooting

### Bot not responding
```bash
sudo systemctl status novaposhta-bot
sudo journalctl -u novaposhta-bot -n 50 --no-pager
```

### Scheduler not syncing / no notifications
```bash
sudo systemctl status novaposhta-scheduler
sudo journalctl -u novaposhta-scheduler -n 50 --no-pager
```

Check that API keys have `auto_sync=True` and `is_active=True`:
```bash
cd /home/user/novaposhta-tracking
source venv/bin/activate
python3 -c "
from app import create_app
app = create_app()
with app.app_context():
    from models import APIKey
    for k in APIKey.query.all():
        print(k.label, 'active:', k.is_active, 'auto_sync:', k.auto_sync)
"
```

### Duplicate/race-condition errors (UNIQUE constraint failed)
This means the scheduler is running in more than one process. Confirm
only `novaposhta-scheduler.service` is running the scheduler, and that
`app.py` itself does **not** start a scheduler:
```bash
grep -n "scheduler\|apscheduler" /home/user/novaposhta-tracking/app.py
# should return nothing
```

### Token not found error
```bash
cat /home/user/novaposhta-tracking/.env | grep TELEGRAM
# should show: TELEGRAM_BOT_TOKEN=your_token_here
```

### Import errors (can't import from app.py)
```bash
cd /home/user/novaposhta-tracking
source venv/bin/activate
pip install -r requirements.txt
python -c "from app import create_app; from models import User, Package"
```

### Bot running twice (conflict)
Only one process may poll a given bot token at a time (e.g. don't run
`telegram_bot.py` on a dev machine while production is also running it -
they'll steal each other's updates).
```bash
ps aux | grep telegram_bot
pkill -f telegram_bot.py   # if a stray manual instance is running
sudo systemctl restart novaposhta-bot
```

### Services not created / install_services.sh silently does nothing
`install_services.sh` only rewrites a unit file if its content changed.
To force recreation:
```bash
sudo rm /etc/systemd/system/novaposhta-bot.service
sudo rm /etc/systemd/system/novaposhta-scheduler.service
bash install_services.sh
sudo systemctl daemon-reload
```

---

## Verify After Reboot

```bash
sudo reboot
# after reboot:
sudo systemctl status novaposhta novaposhta-bot novaposhta-scheduler
```

All three should show `enabled` and `active (running)`.

---

## Production Checklist

- [ ] `TELEGRAM_BOT_TOKEN` set in `.env`
- [ ] Bot and scheduler tested manually before service setup
- [ ] `install_services.sh` run, all 3 services created and enabled
- [ ] All 3 services start on boot
- [ ] Tested after reboot
- [ ] No manual bot/scheduler instances running elsewhere (e.g. dev machine)
- [ ] Logs accessible via journalctl
- [ ] End-to-end notification test passed (status change → Telegram message)