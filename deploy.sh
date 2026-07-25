#!/bin/bash
echo "🚀 Deploying Nova Poshta Tracking..."

cd /home/sysadmin/novaposhta-tracking

git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet
flask db upgrade

# ✅ Install/update systemd services (safe - checks before creating)
bash install_services.sh

# Restart all services
sudo systemctl restart novaposhta novaposhta-bot novaposhta-scheduler

echo "✅ Deploy complete!"
sudo systemctl status novaposhta novaposhta-bot novaposhta-scheduler --no-pager