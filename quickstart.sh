#!/bin/bash

# Quick start script for first-time setup

echo "🚀 Telegram AI Voice Assistant - Quick Start"
echo "============================================"
echo ""

# Check if this is first run
if [ ! -f ".env" ] && [ ! -d "venv" ]; then
    echo "First time setup detected. Running full setup..."
    echo ""
    
    # Make scripts executable
    chmod +x scripts/*.sh
    chmod +x tdlib/install.sh
    chmod +x data/init_directories.sh
    
    # Run setup
    ./scripts/setup.sh
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Setup complete! Starting assistant..."
        ./scripts/start.sh
    else
        echo "❌ Setup failed. Please check the errors above."
        exit 1
    fi
else
    echo "Starting assistant..."
    ./scripts/start.sh
fi