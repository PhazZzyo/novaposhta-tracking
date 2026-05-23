# Change to the user's home directory and run the deployment script ./deploy.sh

cat > /home/user/novaposhta-tracking/deploy.sh << 'EOF'
#!/bin/bash
echo "🚀 Deploying Nova Poshta Tracking..."

cd /home/user/novaposhta-tracking

# Pull latest changes
git pull origin main

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt --quiet

# Run migrations
flask db upgrade

# Restart services
sudo systemctl restart novaposhta
sudo systemctl restart novaposhta-bot 2>/dev/null || true

echo "✅ Deploy complete!"
sudo systemctl status novaposhta --no-pager | head -5
EOF

chmod +x deploy.sh