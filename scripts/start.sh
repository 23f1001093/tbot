#!/bin/bash

# Start Script for Telegram AI Voice Assistant
# Handles environment setup and launches the assistant

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear

echo "╔════════════════════════════════════════════════════════╗"
echo "║        Starting Telegram AI Voice Assistant             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "Please configure your environment variables"
    exit 1
fi

# Export Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Set library path for TDLib
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:$(pwd)/tdlib/lib"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    export DYLD_LIBRARY_PATH="${DYLD_LIBRARY_PATH}:$(pwd)/tdlib/lib"
fi

# Check if TDLib is built
if [ ! -f "tdlib/lib/libtdjson.so" ] && [ ! -f "tdlib/lib/libtdjson.dylib" ]; then
    echo -e "${YELLOW}TDLib not found. Building...${NC}"
    cd tdlib
    ./install.sh
    cd ..
fi

# Clear old logs
echo -e "${YELLOW}Clearing old logs...${NC}"
find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true

# Start the assistant
echo -e "${GREEN}Starting AI Voice Assistant...${NC}"
echo ""

python src/main.py

# Deactivate on exit
deactivate