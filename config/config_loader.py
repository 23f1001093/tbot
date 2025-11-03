"""
Secure configuration loader using environment variables
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Secure configuration management
    Loads from .env file and NEVER exposes secrets in code
    """
    
    def __init__(self, env_file: str = ".env"):
        """Initialize config loader with environment file"""
        self.env_file = env_file
        self.config = {}
        self._load_environment()
        
    def _load_environment(self):
        """Load environment variables from .env file"""
        env_path = Path(self.env_file)
        
        if not env_path.exists():
            # Check for .env.example
            example_path = Path(".env.example")
            if example_path.exists():
                logger.error("❌ .env file not found! Please copy .env.example to .env and add your credentials")
                raise FileNotFoundError(
                    "\n\n⚠️  SECURITY ERROR: No .env file found!\n"
                    "Please do the following:\n"
                    "1. Copy .env.example to .env\n"
                    "2. Add your actual API keys to .env\n"
                    "3. NEVER commit .env to git!\n"
                )
            else:
                raise FileNotFoundError(".env file not found and no .env.example available")
        
        # Load environment variables
        load_dotenv(env_path)
        logger.info("✅ Environment variables loaded from .env")
        
    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration from environment"""
        # Check required variables
        required = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE_NUMBER']
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            raise ValueError(
                f"❌ Missing required environment variables: {', '.join(missing)}\n"
                f"Please add them to your .env file"
            )
        
        return {
            'api_id': int(os.getenv('TELEGRAM_API_ID')),
            'api_hash': os.getenv('TELEGRAM_API_HASH'),
            'phone_number': os.getenv('TELEGRAM_PHONE_NUMBER'),
            'session_name': os.getenv('SESSION_NAME', 'ai_voice_assistant')
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration from environment"""
        return {
            'provider': os.getenv('AI_PROVIDER', 'openai'),
            'model': os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
            'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('AI_MAX_TOKENS', '150')),
            
            'speech_to_text': {
                'provider': os.getenv('STT_PROVIDER', 'google'),
                'language': os.getenv('STT_LANGUAGE', 'en-US'),
                'api_key': os.getenv('GOOGLE_CLOUD_KEY', '')
            },
            
            'text_to_speech': {
                'provider': os.getenv('TTS_PROVIDER', 'gtts'),
                'language': os.getenv('TTS_LANGUAGE', 'en'),
                'voice': os.getenv('TTS_VOICE', 'en-US-Wavenet-D')
            }
        }
    
    def get_full_config(self, config_file: str = "config/config.yaml") -> Dict[str, Any]:
        """
        Get full configuration merging YAML and environment
        Environment variables ALWAYS override YAML values for security
        """
        config = {}
        
        # Load base config from YAML (non-sensitive settings only)
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        
        # Override with environment variables (sensitive data)
        config['telegram'] = self.get_telegram_config()
        config['ai'] = {**config.get('ai', {}), **self.get_ai_config()}
        
        # Add environment-specific settings
        config['environment'] = os.getenv('ENVIRONMENT', 'development')
        config['debug'] = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Validate no secrets in config
        self._validate_no_secrets(config)
        
        return config
    
    def _validate_no_secrets(self, config: Dict, path: str = ""):
        """
        Validate that no actual secrets are hardcoded
        This prevents accidental credential commits
        """
        secret_patterns = [
            'api_key', 'api_hash', 'secret', 'password', 'token',
            'credential', 'private', 'auth'
        ]
        
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if key might contain secret
            key_lower = key.lower()
            if any(pattern in key_lower for pattern in secret_patterns):
                if isinstance(value, str) and value and not value.startswith('${'):
                    # Check if it looks like a real credential
                    if len(value) > 10 and not value.startswith('your_') and not value.startswith('example_'):
                        logger.warning(
                            f"⚠️  Possible hardcoded secret found at {current_path}. "
                            f"Please move to .env file!"
                        )
            
            # Recursive check for nested dicts
            if isinstance(value, dict):
                self._validate_no_secrets(value, current_path)
    
    @staticmethod
    def create_env_template():
        """Create .env.example template if it doesn't exist"""
        template = """# Telegram AI Voice Assistant Configuration
# Copy this file to .env and fill in your actual values
# NEVER commit .env to version control!

# === TELEGRAM CONFIGURATION ===
# Get these from https://my.telegram.org
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890

# === AI PROVIDERS ===
# OpenAI (for GPT models)
OPENAI_API_KEY=sk-...

# Anthropic (for Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google Cloud (for enhanced STT/TTS)
GOOGLE_CLOUD_KEY=AIza...
GOOGLE_APPLICATION_CREDENTIALS=

# === AI SETTINGS ===
AI_PROVIDER=openai  # Options: openai, anthropic, local
AI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=150

# === SPEECH SETTINGS ===
STT_PROVIDER=google  # Options: google, google_cloud, whisper
STT_LANGUAGE=en-US
TTS_PROVIDER=gtts   # Options: gtts, google_cloud, elevenlabs
TTS_LANGUAGE=en
TTS_VOICE=en-US-Wavenet-D

# === SECURITY ===
ENCRYPTION_KEY=
SESSION_STRING=

# === ENVIRONMENT ===
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# === DATABASE ===
DATABASE_URL=sqlite:///data/calls.db

# === OPTIONAL SERVICES ===
REDIS_URL=redis://localhost:6379
WEBHOOK_URL=
"""
        
        example_path = Path(".env.example")
        if not example_path.exists():
            example_path.write_text(template)
            logger.info("✅ Created .env.example template")