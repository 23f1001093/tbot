"""
Session Manager - Handles authentication and session persistence
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manage Telegram sessions securely
    """
    
    def __init__(self, session_name: Optional[str] = None):
        """Initialize session manager"""
        self.session_name = session_name or os.getenv('TELEGRAM_SESSION_NAME', 'ai_assistant')
        self.session_dir = Path('./data/sessions')
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Encryption key from environment
        self.encryption_key = os.getenv('ENCRYPTION_KEY', 'default_key')
        if self.encryption_key == 'default_key':
            logger.warning("⚠️ Using default encryption key. Set ENCRYPTION_KEY in .env!")
        
        self.session_file = self.session_dir / f"{self.session_name}.session"
        self.session_data: Dict[str, Any] = {}
        
        logger.info(f"✅ Session manager initialized: {self.session_name}")
    
    def load_session(self) -> bool:
        """Load existing session"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    encrypted_data = json.load(f)
                    
                # Decrypt session data (simplified - use proper encryption in production)
                self.session_data = self._decrypt_data(encrypted_data)
                
                # Check session validity
                if self._is_session_valid():
                    logger.info("✅ Session loaded successfully")
                    return True
                else:
                    logger.info("Session expired")
                    return False
            
            logger.info("No existing session found")
            return False
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    def save_session(self, session_data: Dict[str, Any]):
        """Save session data securely"""
        try:
            self.session_data = session_data
            self.session_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Encrypt session data
            encrypted_data = self._encrypt_data(self.session_data)
            
            # Save to file
            with open(self.session_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            logger.info("✅ Session saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def clear_session(self):
        """Clear session data"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            self.session_data = {}
            logger.info("Session cleared")
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
    
    def _is_session_valid(self) -> bool:
        """Check if session is still valid"""
        try:
            if 'updated_at' in self.session_data:
                updated = datetime.fromisoformat(self.session_data['updated_at'])
                # Session expires after 30 days
                if datetime.utcnow() - updated > timedelta(days=30):
                    return False
            
            # Check required fields
            required = ['auth_key', 'phone_number']
            return all(field in self.session_data for field in required)
            
        except Exception:
            return False
    
    def _encrypt_data(self, data: Dict) -> Dict:
        """Simple encryption (use proper encryption in production)"""
        # This is a placeholder - use proper encryption like cryptography.fernet
        encrypted = {
            'data': json.dumps(data),
            'hash': hashlib.sha256(
                (json.dumps(data) + self.encryption_key).encode()
            ).hexdigest()
        }
        return encrypted
    
    def _decrypt_data(self, encrypted: Dict) -> Dict:
        """Simple decryption (use proper encryption in production)"""
        # Verify hash
        expected_hash = hashlib.sha256(
            (encrypted['data'] + self.encryption_key).encode()
        ).hexdigest()
        
        if expected_hash != encrypted['hash']:
            raise ValueError("Session data integrity check failed")
        
        return json.loads(encrypted['data'])
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information (without sensitive data)"""
        if not self.session_data:
            return {'status': 'No session'}
        
        return {
            'status': 'Active',
            'phone': self._mask_phone(self.session_data.get('phone_number', '')),
            'updated': self.session_data.get('updated_at', 'Unknown'),
            'valid': self._is_session_valid()
        }
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for logging"""
        if not phone or len(phone) < 7:
            return "***"
        return f"{phone[:3]}***{phone[-4:]}"