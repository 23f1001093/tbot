"""
Input validators and security checks
"""

import re
import os
from typing import Optional

class Validators:
    """Validation utilities"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_api_key(key: str, provider: str) -> bool:
        """Validate API key format"""
        if not key:
            return False
        
        patterns = {
            'openai': r'^sk-[a-zA-Z0-9]{48}$',
            'anthropic': r'^sk-ant-[a-zA-Z0-9]+$',
            'google': r'^AIza[a-zA-Z0-9-_]{35}$'
        }
        
        pattern = patterns.get(provider)
        if pattern:
            return bool(re.match(pattern, key))
        
        return len(key) > 10
    
    @staticmethod
    def validate_environment() -> dict:
        """Validate environment setup"""
        issues = []
        
        # Check required variables
        required = [
            'TELEGRAM_API_ID',
            'TELEGRAM_API_HASH',
            'TELEGRAM_PHONE_NUMBER'
        ]
        
        for var in required:
            if not os.getenv(var):
                issues.append(f"Missing {var}")
        
        # Check if using defaults
        if os.getenv('TELEGRAM_API_ID') == '12345678':
            issues.append("Using default TELEGRAM_API_ID")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32)
        
        # Limit length
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()