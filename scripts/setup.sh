#!/bin/bash

# Complete Setup Script for Telegram AI Voice Assistant
# Run this first to set up everything

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Telegram AI Voice Assistant - Complete Setup        ║"
echo "╚════════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Step 1: Check for .env file
echo ""
echo -e "${BLUE}Step 1: Environment Configuration${NC}"
echo "────────────────────────────────────"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creating .env from template...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your API credentials${NC}"
        
        read -p "Do you want to edit .env now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}✗ No .env.example found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Verify .env is in .gitignore
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo -e "${GREEN}✓ Added .env to .gitignore${NC}"
fi

# Step 2: Install system dependencies
echo ""
echo -e "${BLUE}Step 2: System Dependencies${NC}"
echo "────────────────────────────────────"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${YELLOW}Installing Linux dependencies...${NC}"
    sudo apt-get update
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        portaudio19-dev \
        ffmpeg \
        libopus0 \
        libopus-dev \
        build-essential \
        cmake \
        git
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}Installing macOS dependencies...${NC}"
    brew install portaudio ffmpeg opus cmake
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Step 3: Create Python virtual environment
echo ""
echo -e "${BLUE}Step 3: Python Virtual Environment${NC}"
echo "────────────────────────────────────"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Step 4: Install Python dependencies
echo ""
echo -e "${BLUE}Step 4: Python Dependencies${NC}"
echo "────────────────────────────────────"

echo -e "${YELLOW}Installing Python packages...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Step 5: Build TDLib
echo ""
echo -e "${BLUE}Step 5: TDLib Installation${NC}"
echo "────────────────────────────────────"

if [ ! -f "tdlib/lib/libtdjson.so" ] && [ ! -f "tdlib/lib/libtdjson.dylib" ]; then
    echo -e "${YELLOW}Building TDLib...${NC}"
    cd tdlib
    chmod +x install.sh
    ./install.sh
    cd ..
    echo -e "${GREEN}✓ TDLib built successfully${NC}"
else
    echo -e "${GREEN}✓ TDLib already built${NC}"
fi

# Step 6: Initialize data directories
echo ""
echo -e "${BLUE}Step 6: Data Directories${NC}"
echo "────────────────────────────────────"

cd data
chmod +x init_directories.sh
./init_directories.sh
cd ..

echo -e "${GREEN}✓ Data directories initialized${NC}"

# Step 7: Validate setup
echo ""
echo -e "${BLUE}Step 7: Validation${NC}"
echo "────────────────────────────────────"

python3 << EOF
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Check required environment variables
required = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE_NUMBER']
missing = []

for var in required:
    if not os.getenv(var) or os.getenv(var) in ['12345678', 'your_api_hash_here', '+1234567890']:
        missing.append(var)

if missing:
    print(f"\033[0;31m✗ Missing or default values in .env: {', '.join(missing)}\033[0m")
    sys.exit(1)
else:
    print("\033[0;32m✓ Environment variables validated\033[0m")
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Please configure your .env file with actual values${NC}"
    exit 1
fi

# Step 8: Create start script
echo ""
echo -e "${BLUE}Step 8: Creating Start Script${NC}"
echo "────────────────────────────────────"

cat > start_assistant.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/main.py
EOF

chmod +x start_assistant.sh
echo -e "${GREEN}✓ Start script created${NC}"

# Complete!
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✓ Setup Complete Successfully!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has valid API credentials"
echo "2. Run: ${GREEN}./start_assistant.sh${NC}"
echo ""
echo "The bot will ask for Telegram verification code on first run."
echo ""