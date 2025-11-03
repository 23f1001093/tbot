"""
Main entry point for Telegram AI Voice Assistant
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.tdlib_client import TDLibClient
from src.core.call_manager import CallManager
from src.core.session_manager import SessionManager
from src.ai.speech_to_text import SpeechToText
from src.ai.text_to_speech import TextToSpeech
from src.ai.llm_handler import LLMHandler
from src.ai.conversation import ConversationManager
from src.utils.logger import setup_logging
from src.utils.validators import Validators

# Setup logging
logger = setup_logging()

class TelegramVoiceAssistant:
    """Main application class for Telegram Voice Assistant"""
    
    def __init__(self):
        """Initialize the voice assistant"""
        self.tdlib_client = None
        self.call_manager = None
        self.session_manager = None
        
        # Validate environment
        self._validate_environment()
        
        logger.info("=" * 60)
        logger.info("🤖 Telegram AI Voice Assistant v1.0")
        logger.info("=" * 60)
    
    def _validate_environment(self):
        """Validate environment setup"""
        validator = Validators()
        validation = validator.validate_environment()
        
        if not validation['valid']:
            logger.error("❌ Environment validation failed:")
            for issue in validation['issues']:
                logger.error(f"  - {issue}")
            
            print("\n⚠️  Configuration Issues Detected!")
            print("Please check your .env file and ensure all required values are set.")
            print("\nRequired variables:")
            print("  - TELEGRAM_API_ID (from https://my.telegram.org)")
            print("  - TELEGRAM_API_HASH (from https://my.telegram.org)")
            print("  - TELEGRAM_PHONE_NUMBER (your phone with country code)")
            sys.exit(1)
        
        logger.info("✅ Environment validation passed")
    
    async def initialize_components(self):
        """Initialize all components"""
        logger.info("Initializing components...")
        
        try:
            # Initialize session manager
            self.session_manager = SessionManager()
            
            # Initialize TDLib client
            self.tdlib_client = TDLibClient()
            
            # Initialize AI components
            ai_components = {
                'stt': SpeechToText(),
                'tts': TextToSpeech(),
                'llm': LLMHandler()
            }
            
            # Initialize call manager
            self.call_manager = CallManager(self.tdlib_client, ai_components)
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start(self):
        """Start the voice assistant"""
        try:
            # Print startup banner
            self._print_banner()
            
            # Initialize components
            await self.initialize_components()
            
            # Check for existing session
            if self.session_manager.load_session():
                logger.info("📱 Restored previous session")
            else:
                logger.info("📱 Starting new session")
            
            # Start TDLib client
            logger.info("Starting TDLib client...")
            await self.tdlib_client.start()
            
            logger.info("=" * 60)
            logger.info("🚀 Voice Assistant is RUNNING!")
            logger.info("📞 Ready to receive calls")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)
            
            # Keep running
            await self._keep_alive()
            
        except KeyboardInterrupt:
            logger.info("\n⚠️  Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.shutdown()
    
    async def _keep_alive(self):
        """Keep the assistant running"""
        try:
            # Create an event that never gets set
            stop_event = asyncio.Event()
            await stop_event.wait()
        except KeyboardInterrupt:
            pass
    
    def _print_banner(self):
        """Print startup banner"""
        banner = """
╔════════════════════════════════════════════════════════╗
║                                                        ║
║      🤖 TELEGRAM AI VOICE ASSISTANT                   ║
║                                                        ║
║      • Receives and makes voice calls                 ║
║      • AI-powered conversations                       ║
║      • Real-time speech processing                    ║
║      • Powered by TDLib                              ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down...")
        
        try:
            # Save session if available
            if self.session_manager and self.tdlib_client:
                session_data = {
                    'auth_key': 'session_key',  # Placeholder
                    'phone_number': os.getenv('TELEGRAM_PHONE_NUMBER')
                }
                self.session_manager.save_session(session_data)
            
            # Close TDLib client
            if self.tdlib_client:
                await self.tdlib_client.close()
            
            logger.info("✅ Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if this is first run
    if not os.path.exists(".env"):
        print("\n" + "=" * 60)
        print("⚠️  First Time Setup Detected!")
        print("=" * 60)
        print("\nNo .env file found. Please:")
        print("1. Copy .env.example to .env")
        print("   cp .env.example .env")
        print("\n2. Edit .env with your credentials:")
        print("   - Get API ID and Hash from https://my.telegram.org")
        print("   - Add your phone number with country code")
        print("   - Add OpenAI API key (optional)")
        print("\n3. Run the assistant again:")
        print("   ./scripts/start.sh")
        print("=" * 60 + "\n")
        sys.exit(1)
    
    # Create and start assistant
    assistant = TelegramVoiceAssistant()
    
    try:
        await assistant.start()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the assistant
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)