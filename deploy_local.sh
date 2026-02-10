#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Helper: prompt for a value with optional default
ask() {
    local var_name="$1"
    local prompt="$2"
    local default="$3"
    local value
    if [ -n "$default" ]; then
        read -rp "  $prompt [$default]: " value
        value="${value:-$default}"
    else
        read -rp "  $prompt: " value
    fi
    eval "$var_name=\"$value\""
}

# Interactive setup when .env doesn't exist
if [ ! -f .env ]; then
    # Ensure venv exists for discover_inverter.py dependency
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q pysolarmanv5 2>/dev/null

    python3 setup.py
    if [ $? -ne 0 ] || [ ! -f .env ]; then
        echo -e "${RED}Setup cancelled or failed.${NC}"
        exit 1
    fi
fi

# Load .env but disable Telegram bot for local development
set -a
source .env
set +a
export TELEGRAM_ENABLED=false

# Validate required vars
MISSING=()
[ -z "${INVERTER_IP:-}" ] && MISSING+=("INVERTER_IP")
[ -z "${LOGGER_SERIAL:-}" ] && MISSING+=("LOGGER_SERIAL")

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing required environment variables:${NC}"
    for var in "${MISSING[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Set them in your .env file or run this script again to regenerate it."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

echo -e "${GREEN}Starting Deye Dashboard locally (Telegram bot disabled)...${NC}"
python3 app.py
