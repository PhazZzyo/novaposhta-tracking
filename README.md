# 📦 Nova Poshta Package Tracking System v1.1

A comprehensive web application for tracking Nova Poshta shipments across multiple API accounts with role-based access control, bilingual interface, and advanced filtering.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![Version](https://img.shields.io/badge/version-1.1-orange)

---

## ✨ Features

### 📊 Dashboard
- **4 Clickable Status Cards:**
  - Total Packages (all)
  - Delivering (in transit)
  - Ready for Pickup (arrived at destination)
  - Delivered (picked up by recipient)
- Multi-API key management with auto-sync
- One-click "Sync All" for multiple accounts

### 📦 Package Tracking
- **Bidirectional Tracking:**
  - Outgoing: Packages you sent
  - Incoming: Packages sent to you (requires counterparty_ref)
- **Smart Status Detection:**
  - `StateId = 9` → Ready for pickup
  - `StateId = 10/11` or "Одержано" → Delivered (grey badge)
  - Other → In transit
- Table and Card view modes
- Advanced filtering (direction, status, date range, API key)
- Direct PDF invoice generation

### 👥 User Management
- **3 Role Types:** Admin, Manager, Courier
- User-specific API key tracking
- Customizable preferences per user

### 🌍 Internationalization
- **Bilingual Interface:** 🇺🇦 Ukrainian / 🇬🇧 English
- **Timezone Support:** Europe/Kyiv with automatic DST handling
- User-selectable timezone from 400+ options

### 🎨 Themes
- Light and Dark themes (Material Design inspired)
- Persistent user preference

### 🔧 Admin Features
- **API Key Management:**
  - Import/Export (JSON format) - no more manual entry!
  - Counterparty reference for incoming packages
  - Auto-sync scheduling
- User management
- Activity log with detailed API responses
- Sync cooldown (5 min) to prevent rate limiting

---

## 🚀 Quick Start

### Requirements
- Python 3.9+
- WSL / Linux / macOS

### Installation

```bash
# 1. Clone/Extract
unzip novaposhta-v1.1.zip
cd novaposhta-tracking

# 2. Run setup
./setup.sh

# 3. Start app
source venv/bin/activate
python3 app.py
```

Open **http://localhost:5000**

**Default credentials:** `sysadmin` / `sysadmin`  
⚠️ Change password immediately after first login!

---

## 📖 Usage Guide

### Adding Your First API Key

1. Login as admin
2. Go to **Admin → API Keys → Add API Key**
3. Fill in:
   - **Label:** Friendly name (e.g., "Acme Corp")
   - **API Key:** Your Nova Poshta API key
   - **Sender Identifier:** Your phone number (for outgoing detection)
   - **Counterparty Reference:** UUID for incoming packages (optional)
4. Click **Save**
5. Return to Dashboard and click **Sync**

### Getting Your Counterparty Reference

To track incoming packages:
1. Visit [Nova Poshta API Portal](https://my.novaposhta.ua/)
2. Go to **Settings → API**
3. Copy your **Counterparty Ref** UUID
4. Add it to your API Key settings

### Import/Export API Keys

**Export:**
- Admin → API Keys → Tools → Export
- Downloads JSON file with all keys

**Import:**
- Admin → API Keys → Tools → Import
- Upload JSON file
- Skips duplicates automatically

Perfect for:
- Database resets
- Migrating to new server
- Backup/restore

---

## 🗂️ Project Structure

```
novaposhta-tracking/
├── app.py                    # Main application (Flask + SQLAlchemy)
├── requirements.txt          # Python dependencies
├── setup.sh                  # One-command setup script
├── .env.example              # Environment variables template
├── templates/
│   ├── base.html             # Base layout with navbar
│   ├── login.html
│   ├── dashboard.html        # 4 clickable status cards
│   ├── packages.html         # List with filters
│   ├── package_detail.html
│   ├── settings.html         # User preferences + timezone
│   ├── change_password.html
│   └── admin/
│       ├── users.html
│       ├── add_user.html
│       ├── edit_user.html
│       ├── api_keys.html     # Import/Export UI
│       ├── add_api_key.html  # With counterparty_ref
│       ├── edit_api_key.html
│       ├── log.html
│       └── log_details.html  # API response viewer
└── static/
    ├── css/
    │   ├── style.css         # Main styles
    │   ├── theme-light.css
    │   └── theme-dark.css    # Material Design
    └── js/
        └── app.js            # Sync functions, UI helpers
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env`:

```env
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///novaposhta.db
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/novaposhta_db
```

---

## 👥 User Roles

| Role | Access |
|------|--------|
| **Admin** | Full system access, user management, all API keys |
| **Manager** | View/filter packages, manage assigned API keys |
| **Courier** | View ready-for-pickup packages |

---

## 📊 Package Status Logic

```python
StateId == "9"           → Ready for pickup (green badge)
StateId in ["10", "11"]  → Delivered (grey badge)
StateName contains "Одержано" → Delivered (grey badge)
Everything else          → In transit (yellow badge)
```

---

## 🕐 Timezone Handling

- **Storage:** All timestamps stored in UTC
- **Display:** Converted to user's timezone (default: Europe/Kyiv)
- **DST:** Automatic via pytz
- **Override:** Users can change in Settings (400+ timezones available)

---

## 🔒 Security

- PBKDF2 password hashing
- 30-day session lifetime with "Remember me"
- API keys never exposed in logs
- SQL injection prevention via ORM
- 5-minute sync cooldown prevents API abuse
- Rate limiting with 5-second delay in "Sync All"

---

## 🐛 Troubleshooting

### "Too many requests" error
- System now has 5-second delay between syncs
- If still occurring, increase cooldown in app.py (line ~360)

### Delivered packages not showing
- Check StateId in raw_data column
- Verify `is_delivered` column is TRUE for StateId 10/11

### Timezone showing wrong time
- Check user timezone setting (Settings page)
- Verify pytz is installed: `pip list | grep pytz`

### Import failed
- Ensure JSON file format matches export
- Check for duplicate API keys

---

## 🗺️ Roadmap

- [x] Multi-API key support
- [x] Incoming package tracking
- [x] Import/Export API keys
- [x] Timezone handling
- [x] Grey badges for delivered
- [x] 4 clickable dashboard cards
- [ ] Telegram bot notifications
- [ ] Excel/CSV export
- [ ] Email notifications
- [ ] Auto-deployment

---

## 📝 Changelog

### v1.1 (2026-02-19)
- ✅ Added 4th "Delivered" card to dashboard
- ✅ All dashboard cards now clickable
- ✅ Import/Export API keys (JSON)
- ✅ Timezone support (Europe/Kyiv, auto DST)
- ✅ Delivered packages with grey badges (StateId 10/11)
- ✅ 5-second delay in Sync All (prevents rate limiting)
- ✅ Counterparty reference for incoming packages
- ✅ Detailed error viewer in admin log
- ✅ Fixed direction detection
- ✅ Status filter support (all/delivering/ready/delivered)

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
