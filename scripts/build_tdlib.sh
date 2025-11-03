#!/bin/bash

# TDLib Build Script
# Builds TDLib library for the voice assistant

set -e

echo "Building TDLib for Telegram Voice Assistant..."

cd ../tdlib
chmod +x install.sh
./install.sh

echo "✓ TDLib build complete!"