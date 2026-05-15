# Nova Poshta Tracking App - Deployment Guide

## Prerequisites

- Linux server (Ubuntu 22.04+ recommended)
- Python 3.12+
- Virtual environment set up
- `.env` file configured

---

## 1. Install Gunicorn

```bash
cd /home/sysadmin/np
source venv/bin/activate
pip install gunicorn
```

---

## 2. Test Gunicorn Manually

Before setting up the service, test that gunicorn works:

```bash
cd /home/sysadmin/np
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Open your browser at `http://your-server-ip:5000` - if it works, proceed.

Press `Ctrl+C` to stop.

---

## 3. Create systemd Service

```bash
sudo nano /etc/systemd/system/novaposhta.service
```

Paste this content:

```ini
[Unit]
Description=Nova Poshta Tracking App
After=network.target
Wants=network-online.target

[Service]
User=sysadmin
Group=sysadmin
WorkingDirectory=/home/sysadmin/np
Environment="PATH=/home/sysadmin/np/venv/bin"
EnvironmentFile=/home/sysadmin/np/.env
ExecStart=/home/sysadmin/np/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /home/sysadmin/np/logs/access.log \
    --error-logfile /home/sysadmin/np/logs/error.log \
    --log-level info \
    app:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## 4. Create Logs Directory

```bash
mkdir -p /home/sysadmin/np/logs
```

---

## 5. Enable and Start Service

```bash
# Reload systemd to pick up new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable novaposhta

# Start service now
sudo systemctl start novaposhta

# Check status
sudo systemctl status novaposhta
```

Expected output:
```
● novaposhta.service - Nova Poshta Tracking App
     Loaded: loaded (/etc/systemd/system/novaposhta.service; enabled)
     Active: active (running)
```

---

## 6. Verify It's Running

```bash
# Check if port 5000 is listening
ss -tlnp | grep 5000

# Test with curl
curl http://localhost:5000
```

---

## Management Commands

```bash
# Start
sudo systemctl start novaposhta

# Stop
sudo systemctl stop novaposhta

# Restart (after code changes)
sudo systemctl restart novaposhta

# View live logs
sudo journalctl -u novaposhta -f

# View last 100 lines of logs
sudo journalctl -u novaposhta -n 100

# View access logs
tail -f /home/sysadmin/np/logs/access.log

# View error logs
tail -f /home/sysadmin/np/logs/error.log
```

---

## Updating the App

```bash
# Pull latest code
cd /home/sysadmin/np
git pull

# Activate venv and install new dependencies if any
source venv/bin/activate
pip install -r requirements.txt

# Run migrations if needed
flask db upgrade

# Restart service
sudo systemctl restart novaposhta
```

---

## Troubleshooting

### Service won't start
```bash
# Check detailed error
sudo journalctl -u novaposhta -n 50 --no-pager

# Check if port is already in use
ss -tlnp | grep 5000
```

### App crashes on startup
```bash
# Test manually first
cd /home/sysadmin/np
source venv/bin/activate
python app.py
```

### Permission errors
```bash
# Fix ownership
sudo chown -R sysadmin:sysadmin /home/sysadmin/np
```

### Environment variables not loading
```bash
# Check .env file exists
cat /home/sysadmin/np/.env

# Check EnvironmentFile path in service matches
sudo systemctl cat novaposhta
```

---

## Production Checklist

- [ ] `DEBUG=False` in `.env`
- [ ] `SECRET_KEY` is a strong random string
- [ ] Database backups configured
- [ ] Logs directory created
- [ ] Firewall configured (port 5000 open)
- [ ] Service enabled and running
- [ ] Tested after reboot
