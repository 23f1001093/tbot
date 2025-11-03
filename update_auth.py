import fileinput
import sys

# This script updates the tdlib_client.py to use better auth handling
print("Updating authentication handling...")

# Read the current file
with open('src/core/tdlib_client.py', 'r') as f:
    content = f.read()

# Check if auth_handler import is already there
if 'from .auth_handler import AuthHandler' not in content:
    # Add import after other imports
    content = content.replace(
        'from dotenv import load_dotenv',
        'from dotenv import load_dotenv\nfrom .auth_handler import AuthHandler'
    )
    
    # Add auth_handler initialization
    content = content.replace(
        'self._running = False',
        'self._running = False\n        self.auth_handler = AuthHandler()'
    )

# Write back
with open('src/core/tdlib_client.py', 'w') as f:
    f.write(content)

print("✅ Updated authentication handling")
