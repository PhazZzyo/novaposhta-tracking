    # Nova Poshta Tracking App - Deployment Guide

    ## Prerequisites

    - Linux server (Ubuntu 22.04+ recommended)
    - Python 3.12+
    - Virtual environment set up
    - `.env` file configured (see `.env.example`)

    ---

    ## Architecture (v1.4+)

    The app uses the Flask **application factory pattern**:

    ```
    app.py            → create_app() entry point, module-level app = create_app()
    extensions.py     → db, login_manager, migrate instances
    models.py         → all database models
    routes/           → blueprints (auth, packages, admin, settings, api)
    services/         → business logic (novaposhta.py, notifications.py)
    ```

    This app is deployed alongside two companion processes — the Telegram bot
    and the auto-sync scheduler — see `docs/BOT_DEPLOYMENT.md` for details on
    those. All three are managed by `install_services.sh` / `deploy.sh`.

    ---

    ## 1. Install Gunicorn

    ```bash
    cd /home/user/novaposhta-tracking
    source venv/bin/activate
    pip install gunicorn
    ```

    ---

    ## 2. Test Gunicorn Manually

    ```bash
    cd /home/user/novaposhta-tracking
    source venv/bin/activate
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
    ```

    Open your browser at `http://your-server-ip:5000` - if it works, proceed.

    Press `Ctrl+C` to stop.

    ---

    ## 3. Set Up Flask-Migrate

    The app uses Flask-Migrate for schema changes. `.flaskenv` should contain:

    ```
    FLASK_APP=app:create_app
    ```

    First time only:
    ```bash
    flask db init          # only if migrations/ doesn't exist yet
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

    On every deploy after that, `flask db upgrade` is run automatically by
    `deploy.sh`.

    > If you ever hit "multiple heads" during a merge, resolve with
    > `flask db merge -m "merge heads" <rev1> <rev2>` then `flask db upgrade` -
    > do **not** use `flask db stamp head` to skip a migration, since that marks
    > it as applied without actually running it and can leave tables/columns
    > missing (this bit us once with the `telegram_link_codes` table).

    ---

    ## 4. Create Logs Directory

    ```bash
    mkdir -p /home/user/novaposhta-tracking/logs
    ```

    ---

    ## 5. Install All Services (App, Bot, Scheduler)

    Use the automated installer instead of writing systemd unit files by hand -
    it's idempotent and creates all three services in one go:

    ```bash
    cd /home/user/novaposhta-tracking
    chmod +x install_services.sh
    bash install_services.sh
    ```

    See `docs/BOT_DEPLOYMENT.md` for details on the bot and scheduler services.

    ---

    ## 6. Enable and Start Services

    ```bash
    sudo systemctl enable novaposhta novaposhta-bot novaposhta-scheduler
    sudo systemctl start novaposhta novaposhta-bot novaposhta-scheduler
    sudo systemctl status novaposhta novaposhta-bot novaposhta-scheduler
    ```

    Expected output for the app:
    ```
    ● novaposhta.service - Nova Poshta Tracking App
        Loaded: loaded (/etc/systemd/system/novaposhta.service; enabled)
        Active: active (running)
    ```

    ---

    ## 7. Verify It's Running

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
    tail -f /home/user/novaposhta-tracking/logs/access.log

    # View error logs
    tail -f /home/user/novaposhta-tracking/logs/error.log
    ```

    ---

    ## Updating the App

    The recommended way is the one-command deploy script, which handles
    everything (code, dependencies, migrations, services, restart):

    ```bash
    cd /home/user/novaposhta-tracking
    ./deploy.sh
    ```

    `deploy.sh` does the following:
    1. `git pull origin main`
    2. Installs updated dependencies (`pip install -r requirements.txt`)
    3. Runs `flask db upgrade`
    4. Runs `install_services.sh` (creates/updates systemd services if changed)
    5. Restarts `novaposhta`, `novaposhta-bot`, `novaposhta-scheduler`

    ### Manual equivalent, if needed:
    ```bash
    cd /home/user/novaposhta-tracking
    git pull
    source venv/bin/activate
    pip install -r requirements.txt
    flask db upgrade
    bash install_services.sh
    sudo systemctl restart novaposhta novaposhta-bot novaposhta-scheduler
    ```

    ---

    ## Troubleshooting

    ### Service won't start
    ```bash
    sudo journalctl -u novaposhta -n 50 --no-pager
    ss -tlnp | grep 5000
    ```

    ### App crashes on startup
    ```bash
    cd /home/user/novaposhta-tracking
    source venv/bin/activate
    python app.py
    ```

    ### "no such column" / "no such table" errors
    Usually means a migration wasn't applied. Run:
    ```bash
    flask db upgrade
    ```
    If that reports nothing to do but the column/table is genuinely missing,
    fall back to the ORM's own table creation as a safety net (does not touch
    existing tables/columns, only creates missing ones):
    ```bash
    python3 -c "
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
    "
    ```
    Then investigate why the migration didn't create it (see the Flask-Migrate
    note above about `stamp head`).

    ### Permission errors
    ```bash
    sudo chown -R user:user /home/user/novaposhta-tracking
    ```

    ### Environment variables not loading
    ```bash
    cat /home/user/novaposhta-tracking/.env
    sudo systemctl cat novaposhta   # confirm EnvironmentFile path matches
    ```

    ### Logs directory not writable
    ```bash
    mkdir -p /home/user/novaposhta-tracking/logs
    chown -R user:user /home/user/novaposhta-tracking/logs
    chmod 755 /home/user/novaposhta-tracking/logs
    sudo systemctl restart novaposhta
    ```

    ---

    ## Production Checklist

    - [ ] `DEBUG=False` in `.env`
    - [ ] `SECRET_KEY` is a strong random string
    - [ ] `FLASK_APP=app:create_app` in `.flaskenv`
    - [ ] Database backups configured
    - [ ] Logs directory created and writable
    - [ ] Firewall configured (port 5000 open, or behind nginx on 80/443)
    - [ ] All 3 services (`novaposhta`, `novaposhta-bot`, `novaposhta-scheduler`) enabled and running
    - [ ] Tested after reboot