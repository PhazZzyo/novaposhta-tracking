#!/bin/bash
# install_services.sh
# Creates/updates systemd services for Nova Poshta Tracking App
# Safe to run multiple times - checks before creating

set -e

APP_DIR="/home/sysadmin/novaposhta-tracking"
APP_USER="sysadmin"
APP_GROUP="sysadmin"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Installing/Updating systemd services ===${NC}"

# ============================================================
# Helper function: create or update a service file
# ============================================================
install_service() {
    local service_name=$1
    local service_content=$2
    local service_path="/etc/systemd/system/${service_name}.service"

    if [ -f "$service_path" ]; then
        echo -e "${YELLOW}[${service_name}] Service exists - checking for changes...${NC}"
        # Write to temp file and compare
        echo "$service_content" | sudo tee "/tmp/${service_name}.service.new" > /dev/null
        if ! diff -q "$service_path" "/tmp/${service_name}.service.new" > /dev/null 2>&1; then
            echo -e "${YELLOW}[${service_name}] Changes detected - updating...${NC}"
            sudo mv "/tmp/${service_name}.service.new" "$service_path"
            NEEDS_RELOAD=1
        else
            echo -e "${GREEN}[${service_name}] No changes needed${NC}"
            rm -f "/tmp/${service_name}.service.new"
        fi
    else
        echo -e "${GREEN}[${service_name}] Creating new service...${NC}"
        echo "$service_content" | sudo tee "$service_path" > /dev/null
        NEEDS_RELOAD=1
    fi
}

NEEDS_RELOAD=0

# ============================================================
# 1. Main App Service (Gunicorn)
# ============================================================
APP_SERVICE=$(cat <<EOF
[Unit]
Description=Nova Poshta Tracking App
After=network.target
Wants=network-online.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/gunicorn \\
    --workers 4 \\
    --bind 0.0.0.0:5000 \\
    --timeout 120 \\
    --access-logfile ${APP_DIR}/logs/access.log \\
    --error-logfile ${APP_DIR}/logs/error.log \\
    --log-level info \\
    app:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
)
install_service "novaposhta" "$APP_SERVICE"

# ============================================================
# 2. Telegram Bot Service
# ============================================================
BOT_SERVICE=$(cat <<EOF
[Unit]
Description=Nova Poshta Telegram Bot
After=network.target novaposhta.service
Wants=network-online.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
)
install_service "novaposhta-bot" "$BOT_SERVICE"

# ============================================================
# 3. Scheduler Service (Auto-sync)
# ============================================================
SCHEDULER_SERVICE=$(cat <<EOF
[Unit]
Description=Nova Poshta Auto-Sync Scheduler
After=network.target novaposhta.service

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/python scheduler_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
)
install_service "novaposhta-scheduler" "$SCHEDULER_SERVICE"

# ============================================================
# Reload systemd if any service changed
# ============================================================
if [ "$NEEDS_RELOAD" = "1" ]; then
    echo -e "${YELLOW}Reloading systemd daemon...${NC}"
    sudo systemctl daemon-reload
fi

# ============================================================
# Enable all services (safe if already enabled)
# ============================================================
echo -e "${GREEN}Enabling services...${NC}"
sudo systemctl enable novaposhta novaposhta-bot novaposhta-scheduler

echo -e "${GREEN}=== Services installed/updated successfully ===${NC}"
echo ""
echo "To start all services:"
echo "  sudo systemctl start novaposhta novaposhta-bot novaposhta-scheduler"
echo ""
echo "To restart all services:"
echo "  sudo systemctl restart novaposhta novaposhta-bot novaposhta-scheduler"
echo ""
echo "To check status:"
echo "  sudo systemctl status novaposhta novaposhta-bot novaposhta-scheduler"