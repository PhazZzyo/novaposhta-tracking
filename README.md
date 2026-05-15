# 📦 Nova Poshta Package Tracking System

A comprehensive web application for tracking Nova Poshta shipments across multiple API accounts with role-based access control, Telegram bot notifications, bilingual interface, and advanced filtering.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Version](https://img.shields.io/badge/version-1.3-orange)
![License](https://img.shields.io/badge/license-Private-red)

---

## ✨ Features

### 📊 Dashboard
- **4 Clickable Status Cards:**
  - Total Packages (all)
  - In Transit (delivering)
  - At Branch (ready for pickup)
  - Delivered
- Interactive 30-day trend chart (toggleable metrics)
- Multi-API key management with one-click sync

### 📦 Package Tracking
- **Bidirectional Tracking:**
  - Outgoing: Packages you sent
  - Incoming: Packages sent to you
- **Draft Package System:**
  - Save incomplete packages as drafts
  - Edit and resend failed packages
  - Full validation only on send
- Table and Card view modes
- Advanced filtering (direction, status, date range, API key)
- Direct PDF invoice generation
- Multi-seat package support with dimensions

### 🤖 Telegram Bot (@Orthotrack_bot)
- Account linking via secure code
- Real-time notifications:
  - 📍 Package arrived at branch
  - ✅ Package delivered
- Commands:
  - `/packages` - Packages in transit
  - `/atbranch` - Packages ready for pickup
  - `/settings` - Configure notifications
- Persistent keyboard menu

### 👥 User Management
- **3 Role Types:** Admin, Manager, Courier
- User-specific API key tracking
- Customizable preferences per user

### 🌍 Internationalization
- **Bilingual Interface:** 🇺🇦 Ukrainian / 🇬🇧 English
- **Timezone Support:** Europe/Kyiv with automatic DST
- User-selectable timezone from 400+ options

### 🎨 Themes
- Light and Dark themes
- Persistent user preference
- Toggle from navbar

### 🔧 Admin Features
- **API Key Management:** Import/Export (JSON)
- User management
- Activity log with detailed API responses
- Sync cooldown to prevent rate limiting

---

## 🚀 Quick Start

### Requirements
- Python 3.12+
- Linux / macOS / WSL2

### Installation

```bash
# 1. Clone repository
git clone https://github.com/PhazZzyo/novaposhta-tracking.git
cd novaposhta-tracking

# 2. Run setup
./setup.sh

# 3. Configure environment
cp .env.example .env
nano .env  # Fill in your values

# 4. Start app
source venv/bin/activate
python3 app.py
```

Open **http://localhost:5000**

**Default credentials:** `sysadmin` / `sysadmin`
⚠️ Change password immediately after first login!

### Start Telegram Bot (optional)

```bash
# In a separate terminal
source venv/bin/activate
python3 telegram_bot.py
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Required
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///novaposhta.db

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# Production
DEBUG=False
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/novaposhta_db
```

---

## 🐧 Production Deployment

For running on a Linux server with automatic startup see:

- [App Deployment Guide](docs/APP_DEPLOYMENT.md) - Flask app with Gunicorn + systemd
- [Bot Deployment Guide](docs/BOT_DEPLOYMENT.md) - Telegram bot with systemd

### Quick Deploy

```bash
# Install gunicorn
pip install gunicorn

# Create systemd services
sudo systemctl enable novaposhta novaposhta-bot
sudo systemctl start novaposhta novaposhta-bot

# Check status
sudo systemctl status novaposhta novaposhta-bot
```

---

## 📖 Usage Guide

### Adding Your First API Key

1. Login as admin
2. Go to **Admin → API Keys → Add API Key**
3. Fill in:
   - **Label:** Friendly name (e.g., "Main Sender")
   - **API Key:** Your Nova Poshta API key
   - **Phone:** Sender phone number
4. Click **Save**
5. Return to Dashboard and click **Sync**

### Setting Up Telegram Notifications

1. Find [@Orthotrack_bot](https://t.me/Orthotrack_bot) in Telegram
2. Send `/start` to get a linking code
3. In the web app go to **Settings → Telegram Bot**
4. Enter the linking code
5. Done! You'll now receive package notifications

### Creating a Draft Package

1. Go to **Packages → Create Package**
2. Fill in recipient details
3. Click **Save as Draft** to save without sending
4. Later, click **Edit** on the draft
5. Complete the form and click **Send**

### Import/Export API Keys

**Export:** Admin → API Keys → Export → Downloads JSON

**Import:** Admin → API Keys → Import → Upload JSON

---

## 🗂️ Project Structure

```
novaposhta-tracking/
├── app.py                    # Main Flask application
├── telegram_bot.py           # Telegram bot (separate process)
├── translations.py           # EN/UK translations
├── requirements.txt          # Python dependencies
├── setup.sh                  # One-command setup script
├── .env.example              # Environment variables template
├── docs/
│   ├── APP_DEPLOYMENT.md     # Flask app deployment guide
│   └── BOT_DEPLOYMENT.md     # Telegram bot deployment guide
├── templates/
│   ├── base.html             # Base layout with navbar
│   ├── login.html
│   ├── dashboard.html        # Status cards + trend chart
│   ├── packages.html         # Package list with filters
│   ├── package_detail.html
│   ├── create_package_modal.html
│   ├── telegram_settings.html
│   ├── settings.html
│   └── admin/
│       ├── users.html
│       ├── api_keys.html
│       └── log.html
└── static/
    ├── css/
    │   ├── style.css
    │   ├── theme-light.css
    │   └── theme-dark.css
    └── js/
```

---

## 👥 User Roles

| Role | Access |
|------|--------|
| **Admin** | Full access, user management, all API keys |
| **Manager** | View/filter packages, assigned API keys |
| **Courier** | View ready-for-pickup packages |

---

## 🔒 Security

- PBKDF2 password hashing
- 30-day session lifetime with "Remember me"
- API keys never exposed in logs
- SQL injection prevention via ORM
- Sync cooldown prevents API abuse
- Telegram linking via expiring codes (10 min)

---

## 🐛 Troubleshooting

### App won't start
```bash
source venv/bin/activate
python3 app.py  # Check error output
```

### Bot not responding
```bash
# Check token in .env
cat .env | grep TELEGRAM

# Run manually to see errors
source venv/bin/activate
python3 telegram_bot.py
```

### Packages not syncing
- Check API key is valid in Admin → API Keys
- Check sync logs in Admin → Log
- Verify Nova Poshta API is accessible

### Timezone showing wrong time
- Check user timezone in Settings
- Default timezone: Europe/Kyiv

---

## 🗺️ Roadmap

- [x] Multi-API key support
- [x] Bidirectional package tracking
- [x] Import/Export API keys
- [x] Timezone support
- [x] Dark/Light themes
- [x] Dashboard trend chart
- [x] Draft package system
- [x] Multi-seat packages
- [x] Telegram bot notifications
- [x] systemd deployment
- [ ] Excel/CSV export
- [ ] Email notifications
- [ ] Package templates
- [ ] Client management UI

---

## 📝 Changelog

### v1.3 (2026-05-15) - Current
- ✅ Telegram bot integration (@Orthotrack_bot)
- ✅ Real-time notifications (at branch, delivered)
- ✅ Bot commands: /packages, /atbranch, /settings
- ✅ Persistent keyboard menu in bot
- ✅ systemd deployment guides
- ✅ Draft package system (save → edit → send)
- ✅ Multi-seat package support with dimensions
- ✅ Dark theme fixes (data-theme attribute)
- ✅ Navbar theme toggle (saved to DB)

### v1.2 (2026-03-06)
- ✅ Package creation with Nova Poshta API
- ✅ Auto-fill sender profile from API key
- ✅ Client quick-select
- ✅ Dashboard trend chart (30 days)
- ✅ Modern card/table redesign
- ✅ Invoice button smart enable/disable

### v1.1 (2026-02-19)
- ✅ 4 clickable dashboard cards
- ✅ Import/Export API keys (JSON)
- ✅ Timezone support (Europe/Kyiv)
- ✅ Delivered packages with grey badges
- ✅ Status filter support

### v1.0 (2026-02-17)
- Initial release
- Basic package tracking
- User management
- Bilingual interface

---

## 📄 License

Private project. All rights reserved.

---

## 🤝 Support

For issues or questions, contact the system administrator.

**Powered by Flask & Nova Poshta API**