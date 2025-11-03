#!/bin/bash

# Dependencies Installation Script
# Installs all required system and Python dependencies

set -e

echo "Installing dependencies for Telegram Voice Assistant..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Linux dependencies..."
    
    # Update package list
    sudo apt-get update
    
    # System dependencies
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        build-essential \
        cmake \
        git \
        wget \
        curl
    
    # Audio dependencies
    sudo apt-get install -y \
        portaudio19-dev \
        ffmpeg \
        libopus0 \
        libopus-dev \
        libasound2-dev \
        libpulse-dev
    
    # Additional tools
    sudo apt-get install -y \
        sox \
        libsox-fmt-all
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing macOS dependencies..."
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install dependencies
    brew install \
        python3 \
        cmake \
        git \
        wget \
        portaudio \
        ffmpeg \
        opus \
        sox
fi

# Python dependencies
echo "Installing Python packages..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Additional useful packages
pip install \
    ipython \
    jupyter \
    black \
    flake8 \
    pytest-asyncio \
    pytest-cov

echo "✓ All dependencies installed successfully!"