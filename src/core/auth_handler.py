"""
Authentication handler for TDLib
Handles verification codes and 2FA
"""

import asyncio
import logging
from typing import Optional
import sys

logger = logging.getLogger(__name__)

class AuthHandler:
    """Handle authentication flow"""
    
    def __init__(self):
        self.waiting_for_code = False
        self.waiting_for_password = False
        self.code_queue = asyncio.Queue()
        self.password_queue = asyncio.Queue()
    
    async def request_verification_code(self) -> str:
        """Request verification code from user"""
        self.waiting_for_code = True
        
        # Clear terminal line
        sys.stdout.write('\r' + ' '*80 + '\r')
        sys.stdout.flush()
        
        print("\n" + "="*50)
        print("📲 VERIFICATION CODE REQUIRED")
        print("="*50)
        print("Check your Telegram app for the code")
        print("(It may come as a message from Telegram)")
        
        # Get input in a way that doesn't block
        loop = asyncio.get_event_loop()
        code = await loop.run_in_executor(
            None, 
            lambda: input("Enter code (5 digits): ").strip()
        )
        
        self.waiting_for_code = False
        return code
    
    async def request_2fa_password(self) -> str:
        """Request 2FA password from user"""
        self.waiting_for_password = True
        
        print("\n" + "="*50)
        print("🔐 2FA PASSWORD REQUIRED")
        print("="*50)
        
        # Get password input
        import getpass
        loop = asyncio.get_event_loop()
        password = await loop.run_in_executor(
            None,
            lambda: getpass.getpass("Enter 2FA password: ")
        )
        
        self.waiting_for_password = False
        return password
