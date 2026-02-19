# 📦 Nova Poshta Tracking System

A web application for tracking Nova Poshta shipments across multiple API accounts with role-based access control, light/dark themes, and full Ukrainian/English interface.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

---

## ✨ Features

- **Multi-account tracking** — manage multiple Nova Poshta API keys
- **Auto-sync** — automatic package sync every 30 minutes (9:00–18:00)
- **Manual sync** — on-demand sync with 5-minute cooldown
- **Smart direction detection** — automatically identifies incoming vs outgoing packages
- **Role-based access** — Admin, Manager, Courier roles
- **Bilingual interface** — 🇺🇦 Ukrainian / 🇬🇧 English, switchable per user
- **Light & Dark themes** — Material Design inspired dark theme
- **Two view modes** — Table and Card views
- **Advanced filtering** — by direction, API key, status, date range
- **Package details** — full shipment info with recipient contact
- **Invoice generation** — direct link to Nova Poshta PDF invoice
- **SQLite / PostgreSQL** — SQLite for development, PostgreSQL for production

---

## 🚀 Quick Start

### Requirements

- Python 3.9+
- WSL / Linux / macOS

### Installation

```bash
# 1. Extract the project
unzip novaposhta-tracking-v2.zip
mv np-clean novaposhta-tracking
cd novaposhta-tracking

# 2. Run setup (creates venv, installs deps, generates SECRET_KEY)
./setup.sh

# 3. Activate and run
source venv/bin/activate
python3 app.py
```

Open **http://localhost:5000**

**Default login:** `sysadmin` / `sysadmin`
> ⚠️ Change the default password immediately after first login!

---

## 🗂️ Project Structure

```
novaposhta-tracking/
├── app.py                  # Main application (routes, models, API client)
├── requirements.txt        # Python dependencies
├── setup.sh                # One-command setup script
├── .env.example            # Environment variable template
├── .gitignore
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout with navbar & language switcher
│   ├── login.html
│   ├── dashboard.html
│   ├── packages.html       # Package list (table & card views)
│   ├── package_detail.html # Package details modal content
│   ├── settings.html       # User preferences
│   ├── change_password.html
│   └── admin/
│       ├── users.html
│       ├── add_user.html
│       ├── edit_user.html
│       ├── api_keys.html
│       ├── add_api_key.html
│       └── edit_api_key.html
│
└── static/
    ├── css/
    │   ├── style.css        # Main styles
    │   ├── theme-light.css  # Light theme
    │   └── theme-dark.css   # Dark theme (Material Design)
    └── js/
        └── app.js           # Sync, toast notifications, UI helpers
```

---

## ⚙️ Configuration

The setup script auto-generates a `SECRET_KEY`. To customise, edit `.env`:

```env
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=sqlite:///novaposhta.db
```

### Using PostgreSQL (production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/novaposhta_db
```

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access — users, API keys, all packages, settings |
| **Manager** | View & filter packages across assigned API keys |
| **Courier** | View packages ready for pickup |

- Admin interface defaults to **English**
- Manager / Courier interface defaults to **Ukrainian**
- Each user can switch language independently (🇺🇦 / 🇬🇧 in navbar)

---

## 🔑 Adding Your First API Key

1. Log in as `sysadmin`
2. Go to **Admin → API Keys → Add API Key**
3. Fill in:
   - **Label** — friendly name e.g. "Acme Corp"
   - **API Key** — your Nova Poshta API key
   - **Sender Identifier** — your phone number (used to detect outgoing packages)
4. Click **Add API Key**
5. Go to **Dashboard** and click **Sync**

---

## 🌐 Nova Poshta API

- Endpoint: `https://api.novaposhta.ua/v2.0/json/`
- Method used: `InternetDocument / getDocumentList`
- Get your API key at: [devcenter.novaposhta.ua](https://devcenter.novaposhta.ua/)

---

## 🐳 Docker (optional)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

> Requires `docker-compose.yml` — add PostgreSQL service if needed.

---

## 🔐 Security

- Passwords hashed with Werkzeug PBKDF2
- Session lifetime: 30 days (with "Remember me")
- API keys stored in database, never in code or logs
- `.env` excluded from Git
- SQL injection prevented via SQLAlchemy ORM
- 5-minute sync cooldown prevents API abuse

---

## 🗺️ Roadmap

- [x] Multi-API key support
- [x] Role-based access control
- [x] Light / Dark themes
- [x] Ukrainian / English interface
- [x] Table & Card views
- [x] Invoice PDF link
- [ ] Telegram bot notifications (Stage 2)
- [ ] Export to Excel / CSV
- [ ] Email notifications
- [ ] Auto-deployment to Svai.net

---

## 📄 License

Private project. All rights reserved.
