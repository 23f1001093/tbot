#!/bin/bash

# TDLib Installation Script
# Builds TDLib from source with all dependencies

set -e  # Exit on error

echo "════════════════════════════════════════════════════════"
echo "       TDLib Installation for Voice Assistant"
echo "════════════════════════════════════════════════════════"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${GREEN}✓ Linux detected${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    echo -e "${GREEN}✓ macOS detected${NC}"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    echo -e "${GREEN}✓ Windows detected${NC}"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

# Install dependencies based on OS
echo -e "${YELLOW}Installing system dependencies...${NC}"

if [ "$OS" == "linux" ]; then
    sudo apt-get update
    sudo apt-get install -y \
        make \
        git \
        zlib1g-dev \
        libssl-dev \
        gperf \
        cmake \
        clang \
        libc++-dev \
        libc++abi-dev
elif [ "$OS" == "mac" ]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install gperf cmake openssl
elif [ "$OS" == "windows" ]; then
    echo -e "${YELLOW}Please install Visual Studio with C++ support${NC}"
    echo -e "${YELLOW}And vcpkg for dependencies management${NC}"
fi

# Create directories
mkdir -p build lib

# Clone TDLib if not exists
if [ ! -d "td" ]; then
    echo -e "${YELLOW}Cloning TDLib repository...${NC}"
    git clone https://github.com/tdlib/td.git
    echo -e "${GREEN}✓ TDLib cloned${NC}"
else
    echo -e "${YELLOW}Updating TDLib repository...${NC}"
    cd td
    git pull
    cd ..
    echo -e "${GREEN}✓ TDLib updated${NC}"
fi

# Build TDLib
echo -e "${YELLOW}Building TDLib (this will take 10-20 minutes)...${NC}"

cd build
rm -rf *  # Clean previous build

if [ "$OS" == "windows" ]; then
    cmake -DCMAKE_BUILD_TYPE=Release ../td
    cmake --build . --config Release
else
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=../lib ../td
    cmake --build . -- -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
fi

echo -e "${GREEN}✓ TDLib built successfully${NC}"

# Install libraries
echo -e "${YELLOW}Installing libraries...${NC}"

if [ "$OS" == "windows" ]; then
    cp Release/*.dll ../lib/
    cp Release/*.lib ../lib/
else
    make install
fi

# Create Python bindings info
cat > ../lib/tdlib_info.json << EOF
{
    "version": "1.8.0",
    "build_date": "$(date -u +"%Y-%m-%d %H:%M:%S")",
    "os": "$OS",
    "library_path": "$(pwd)/../lib"
}
EOF

echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ TDLib installation complete!${NC}"
echo -e "${GREEN}Library location: $(pwd)/../lib${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

cd ..