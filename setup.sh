#!/bin/bash
set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo "========================================"
echo " Nova Poshta Tracking — Setup"
echo "========================================"

command -v python3 >/dev/null || { echo -e "${RED}python3 not found${NC}"; exit 1; }

echo -e "${GREEN}[1/4] Creating virtual environment...${NC}"
[ -d venv ] && rm -rf venv
python3 -m venv venv

echo -e "${GREEN}[2/4] Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo -e "${GREEN}[3/4] Creating .env...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    SK=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/change-this-to-a-long-random-string/$SK/" .env
    echo -e "${GREEN}   .env created with auto-generated SECRET_KEY${NC}"
else
    echo -e "${YELLOW}   .env already exists, skipping${NC}"
fi

echo -e "${GREEN}[4/4] Initialising database...${NC}"
python3 app.py &
APP_PID=$!
sleep 3
kill $APP_PID 2>/dev/null || true

echo ""
echo "========================================"
echo -e "${GREEN} Setup complete!${NC}"
echo "========================================"
echo ""
echo " Run the app:"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo " Then open: http://localhost:5000"
echo " Login:     sysadmin / sysadmin"
echo -e " ${YELLOW}⚠  Change password on first login!${NC}"
echo "========================================"
