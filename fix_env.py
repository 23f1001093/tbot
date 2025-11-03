import os
from dotenv import dotenv_values

# Read current values
config = dotenv_values(".env")

# Clean values
api_id = config.get('TELEGRAM_API_ID', '').strip("'\"")
api_hash = config.get('TELEGRAM_API_HASH', '').strip("'\"")
phone = config.get('TELEGRAM_PHONE_NUMBER', '').strip("'\"")

# Write clean .env
with open('.env', 'w') as f:
    f.write(f"# Telegram Credentials\n")
    f.write(f"TELEGRAM_API_ID={api_id}\n")
    f.write(f"TELEGRAM_API_HASH={api_hash}\n")
    f.write(f"TELEGRAM_PHONE_NUMBER={phone}\n")
    f.write(f"\n# Other settings\n")
    
    # Copy other settings
    for key, value in config.items():
        if key not in ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE_NUMBER']:
            f.write(f"{key}={value}\n")

print("✅ Fixed .env file - removed quotes/apostrophes")
print(f"API_ID: {api_id}")
print(f"API_HASH: {api_hash[:4]}...{api_hash[-4:]}")
print(f"PHONE: {phone}")
