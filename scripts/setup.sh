#!/bin/bash

# Secure setup script with credential management

set -e

echo "🔒 Secure Telegram AI Voice Assistant Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your API credentials${NC}"
        
        # Open editor if available
        if command -v nano &> /dev/null; then
            read -p "Do you want to edit .env now? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                nano .env
            fi
        fi
    else
        echo -e "${RED}❌ No .env.example found!${NC}"
        exit 1
    fi
fi

# Verify .env is in .gitignore
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.env$" .gitignore; then
        echo ".env" >> .gitignore
        echo -e "${GREEN}✅ Added .env to .gitignore${NC}"
    fi
else
    echo ".env" > .gitignore
    echo -e "${GREEN}✅ Created .gitignore with .env${NC}"
fi

# Check for exposed credentials in git history
if [ -d ".git" ]; then
    echo "Checking for exposed credentials in git history..."
    
    # Check if .env was ever committed
    if git ls-files .env --error-unmatch 2>/dev/null; then
        echo -e "${RED}⚠️  WARNING: .env is tracked by git!${NC}"
        echo "Run: git rm --cached .env"
        echo "Then commit the change"
    fi
    
    # Search for potential secrets in committed files
    PATTERNS="api_key|api_hash|token|secret|password"
    if git grep -i -E "$PATTERNS" 2>/dev/null | grep -v ".env.example"; then
        echo -e "${YELLOW}⚠️  Potential secrets found in repository${NC}"
        echo "Please review and move them to .env"
    fi
fi

# Validate .env contents
echo "Validating .env configuration..."

# Check required variables
REQUIRED_VARS="TELEGRAM_API_ID TELEGRAM_API_HASH TELEGRAM_PHONE_NUMBER"
MISSING_VARS=""

for VAR in $REQUIRED_VARS; do
    if ! grep -q "^$VAR=" .env; then
        MISSING_VARS="$MISSING_VARS $VAR"
    fi
done

if [ -n "$MISSING_VARS" ]; then
    echo -e "${RED}❌ Missing required variables in .env:${NC}"
    echo "$MISSING_VARS"
    echo "Please add them to your .env file"
    exit 1
else
    echo -e "${GREEN}✅ All required variables present${NC}"
fi

# Continue with normal setup
echo ""
echo "Installing Python dependencies..."
pip install python-dotenv  # Add this to requirements.txt
pip install -r requirements.txt

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Secure setup complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure your .env has valid API credentials"
echo "2. Run: python src/main_secure.py"
echo ""
echo -e "${YELLOW}Remember: NEVER commit .env to version control!${NC}"