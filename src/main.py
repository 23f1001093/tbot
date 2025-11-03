"""
Main Application with Secure Configuration
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.tdlib_client import TDLibClient
from src.core.call_manager import CallManager
from src.ai.speech_to_text import SpeechToText
from src.ai.text_to_speech import TextToSpeech
from src.ai.llm_handler import LLMHandler
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class TelegramVoiceAssistant:
    """Main application class with secure configuration"""
    
    def __init__(self):
        """Initialize with secure configuration"""
        # Check for .env file FIRST
        self._check_env_file()
        
        # Load configuration securely
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.get_full_config()
        
        # Mask sensitive data in logs
        self._log_config_safely()
        
        self.tdlib_client = None
        self.call_manager = None
    
    def _check_env_file(self):
        """Check if .env file exists and warn if not"""
        env_path = Path(".env")
        example_path = Path(".env.example")
        
        if not env_path.exists():
            print("\n" + "=" * 60)
            print("⚠️  SECURITY WARNING: No .env file found!")
            print("=" * 60)
            print("\nTo set up your credentials securely:")
            print("1. Copy .env.example to .env:")
            print("   cp .env.example .env")
            print("\n2. Edit .env and add your API keys:")
            print("   nano .env")
            print("\n3. Make sure .env is in .gitignore:")
            print("   echo '.env' >> .gitignore")
            print("\n4. NEVER commit .env to Git!")
            print("=" * 60 + "\n")
            
            # Create .env.example if it doesn't exist
            if not example_path.exists():
                ConfigLoader.create_env_template()
                print("✅ Created .env.example for you")
            
            sys.exit(1)
    
    def _log_config_safely(self):
        """Log configuration without exposing secrets"""
        safe_config = {
            'telegram': {
                'api_id': '***' + str(self.config['telegram']['api_id'])[-4:],
                'api_hash': self._mask_string(self.config['telegram']['api_hash']),
                'phone_number': self._mask_phone(self.config['telegram']['phone_number'])
            },
            'ai': {
                'provider': self.config['ai']['provider'],
                'model': self.config['ai']['model'],
                'has_api_key': bool(self.config['ai'].get('api_key'))
            },
            'environment': self.config.get('environment', 'unknown')
        }
        
        logger.info(f"Configuration loaded (masked): {safe_config}")
    
    def _mask_string(self, s: str) -> str:
        """Mask sensitive string"""
        if not s:
            return "NOT_SET"
        if len(s) <= 8:
            return "*" * len(s)
        return s[:4] + "*" * (len(s) - 8) + s[-4:]
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        if not phone:
            return "NOT_SET"
        return phone[:3] + "*" * (len(phone) - 7) + phone[-4:]
    
    async def initialize_components(self):
        """Initialize all components"""
        logger.info("Initializing components...")
        
        # Validate required credentials
        self._validate_credentials()
        
        # Initialize TDLib client
        self.tdlib_client = TDLibClient(self.config)
        
        # Initialize AI components
        ai_components = {
            'stt': SpeechToText(self.config['ai']['speech_to_text']),
            'tts': TextToSpeech(self.config['ai']['text_to_speech']),
            'llm': LLMHandler(self.config['ai'])
        }
        
        # Initialize call manager
        self.call_manager = CallManager(self.tdlib_client, ai_components)
        
        logger.info("✅ All components initialized securely")
    
    def _validate_credentials(self):
        """Validate that required credentials are present"""
        errors = []
        
        # Check Telegram credentials
        if not self.config['telegram']['api_id']:
            errors.append("TELEGRAM_API_ID not set in .env")
        if not self.config['telegram']['api_hash']:
            errors.append("TELEGRAM_API_HASH not set in .env")
        if not self.config['telegram']['phone_number']:
            errors.append("TELEGRAM_PHONE_NUMBER not set in .env")
        
        # Check AI credentials (warn only)
        if self.config['ai']['provider'] == 'openai' and not self.config['ai'].get('api_key'):
            logger.warning("⚠️  OpenAI API key not set - will use fallback responses")
        
        if errors:
            print("\n❌ Missing required credentials:")
            for error in errors:
                print(f"  - {error}")
            print("\nPlease add them to your .env file")
            sys.exit(1)
    
    async def start(self):
        """Start the voice assistant"""
        try:
            # Show security reminder
            if self.config.get('environment') == 'development':
                logger.warning("🔧 Running in DEVELOPMENT mode")
            
            # Initialize components
            await self.initialize_components()
            
            # Start TDLib client
            await self.tdlib_client.start()
            
            logger.info("=" * 60)
            logger.info("🚀 Voice Assistant is running SECURELY!")
            logger.info("🔒 Credentials loaded from .env file")
            logger.info("📞 Ready to receive calls")
            logger.info("=" * 60)
            
            # Keep running
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            logger.info("\n⚠️ Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down...")
        
        if self.tdlib_client:
            await self.tdlib_client.close()
        
        logger.info("✅ Shutdown complete")

async def main():
    """Main entry point with security checks"""
    
    # Security banner
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     🔒 SECURE TELEGRAM AI VOICE ASSISTANT            ║
    ║                                                       ║
    ║     • All credentials in .env file                   ║
    ║     • .env is git-ignored                           ║
    ║     • No secrets in code                            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Create and start assistant
    assistant = TelegramVoiceAssistant()
    await assistant.start()

if __name__ == "__main__":
    asyncio.run(main())