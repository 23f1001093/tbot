"""
TDLib Client - Fixed for proper parameter passing
"""

import os
import asyncio
import json
import logging
from typing import Dict, Optional, Any, Callable
from pathlib import Path
import ctypes
from ctypes import CDLL, c_void_p, c_char_p, c_double
from datetime import datetime
from dotenv import load_dotenv
from .auth_handler import AuthHandler

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TDLibClient:
    """TDLib client for Telegram integration"""
    
    def __init__(self):
        """Initialize TDLib client with environment variables"""
        # Load credentials as integers/strings
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '')
        self.phone_number = os.getenv('TELEGRAM_PHONE_NUMBER', '')
        
        # Debug logging
        logger.info(f"Initializing with API ID: {self.api_id}")
        logger.info(f"API Hash present: {'Yes' if self.api_hash else 'No'}")
        
        # Validate
        if self.api_id == 0 or not self.api_hash:
            raise ValueError("Invalid Telegram credentials")
        
        self.client = None
        self.authorized = False
        self.call_handlers = {}
        self.active_calls = {}
        self._running = False
        self.auth_handler = AuthHandler()
        
        # Create data directories
        Path('./data/tdlib/db').mkdir(parents=True, exist_ok=True)
        Path('./data/tdlib/files').mkdir(parents=True, exist_ok=True)
        
        # Load TDLib
        self._load_tdlib()
    
    def _load_tdlib(self):
        """Load TDLib shared library"""
        try:
            import sys
            # Try multiple possible paths
            possible_paths = [
                './tdlib/lib/libtdjson.dylib',  # macOS in project
                './tdlib/build/libtdjson.dylib', # macOS build dir
                './tdlib/lib/libtdjson.so',      # Linux
                './tdlib/build/libtdjson.so',    # Linux build dir
                '/usr/local/lib/libtdjson.dylib', # System macOS
                '/usr/local/lib/libtdjson.so'     # System Linux
            ]
            
            lib_path = None
            for path in possible_paths:
                if Path(path).exists():
                    lib_path = path
                    break
            
            if not lib_path:
                raise FileNotFoundError(f"TDLib not found. Tried: {possible_paths}")
            
            logger.info(f"Loading TDLib from: {lib_path}")
            self.tdjson = CDLL(lib_path)
            self._setup_functions()
            logger.info("✅ TDLib loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load TDLib: {e}")
            raise
    
    def _setup_functions(self):
        """Set up TDLib function signatures"""
        self.tdjson.td_json_client_create.restype = c_void_p
        self.tdjson.td_json_client_create.argtypes = []
        
        self.tdjson.td_json_client_send.restype = None
        self.tdjson.td_json_client_send.argtypes = [c_void_p, c_char_p]
        
        self.tdjson.td_json_client_receive.restype = c_char_p
        self.tdjson.td_json_client_receive.argtypes = [c_void_p, c_double]
        
        self.tdjson.td_json_client_execute.restype = c_char_p
        self.tdjson.td_json_client_execute.argtypes = [c_void_p, c_char_p]
        
        self.tdjson.td_json_client_destroy.restype = None
        self.tdjson.td_json_client_destroy.argtypes = [c_void_p]
    
    async def start(self):
        """Start TDLib client"""
        logger.info("Starting TDLib client...")
        
        # Create client
        self.client = self.tdjson.td_json_client_create()
        self._running = True
        
        # Start update receiver
        asyncio.create_task(self._receive_updates())
        
        # Wait a moment
        await asyncio.sleep(0.5)
        
        # Set TDLib parameters - THIS IS THE CRITICAL PART
        tdlib_params = {
            '@type': 'setTdlibParameters',
            'parameters': {
                'use_test_dc': False,
                'database_directory': './data/tdlib/db',
                'files_directory': './data/tdlib/files',
                'use_file_database': True,
                'use_chat_info_database': True,
                'use_message_database': True,
                'use_secret_chats': False,
                'api_id': self.api_id,  # MUST be an integer
                'api_hash': self.api_hash,  # MUST be a string
                'system_language_code': 'en',
                'device_model': 'Desktop',
                'system_version': 'Unknown',
                'application_version': '1.0.0',
                'enable_storage_optimizer': True
            }
        }
        
        logger.info(f"Sending parameters with api_id: {self.api_id}")
        await self._send(tdlib_params)
        
        # Wait for parameter confirmation
        await asyncio.sleep(1)
        
        logger.info("TDLib client initialized")
    
    async def _receive_updates(self):
        """Receive updates from Telegram"""
        request_code = False
        
        while self._running:
            if self.client:
                try:
                    result = self.tdjson.td_json_client_receive(
                        self.client, c_double(1.0)
                    )
                    if result:
                        update = json.loads(result.decode('utf-8'))
                        
                        # Handle different update types
                        update_type = update.get('@type')
                        
                        if update_type == 'updateAuthorizationState':
                            auth_state = update['authorization_state']['@type']
                            logger.info(f"Auth state: {auth_state}")
                            
                            if auth_state == 'authorizationStateWaitTdlibParameters':
                                # Should not reach here if parameters were sent correctly
                                logger.error("TDLib still waiting for parameters!")
                                
                            elif auth_state == 'authorizationStateWaitEncryptionKey':
                                # Send empty encryption key
                                await self._send({
                                    '@type': 'checkDatabaseEncryptionKey',
                                    'encryption_key': ''
                                })
                                
                            elif auth_state == 'authorizationStateWaitPhoneNumber':
                                # Send phone number
                                logger.info(f"Sending phone number: {self.phone_number[:3]}***")
                                await self._send({
                                    '@type': 'setAuthenticationPhoneNumber',
                                    'phone_number': self.phone_number,
                                    'settings': {
                                        '@type': 'phoneNumberAuthenticationSettings',
                                        'allow_flash_call': False,
                                        'allow_missed_call': False,
                                        'is_current_phone_number': False,
                                        'allow_sms_retriever_api': False
                                    }
                                })
                                
                            elif auth_state == 'authorizationStateWaitCode' and not request_code:
                                request_code = True
                                # Get code from user
                                code = input("\n📲 Enter verification code: ")
                                await self._send({
                                    '@type': 'checkAuthenticationCode',
                                    'code': code
                                })
                                
                            elif auth_state == 'authorizationStateWaitPassword':
                                # Get 2FA password
                                password = input("\n🔐 Enter 2FA password: ")
                                await self._send({
                                    '@type': 'checkAuthenticationPassword',
                                    'password': password
                                })
                                
                            elif auth_state == 'authorizationStateReady':
                                self.authorized = True
                                logger.info("✅ Successfully logged in!")
                                
                        elif update_type == 'updateCall':
                            await self._handle_call_update(update['call'])
                            
                        elif update_type == 'error':
                            logger.error(f"TDLib error: {update.get('message')}")
                            
                except Exception as e:
                    logger.error(f"Error receiving update: {e}")
                    
            await asyncio.sleep(0.01)
    
    async def _handle_call_update(self, call: Dict):
        """Handle call updates"""
        call_id = call['id']
        state = call['state']['@type']
        
        logger.info(f"📞 Call {call_id} - State: {state}")
        
        if state == 'callStatePending' and not call.get('is_outgoing'):
            logger.info(f"📲 Incoming call {call_id}")
            if 'on_incoming_call' in self.call_handlers:
                await self.call_handlers['on_incoming_call'](call)
        elif state == 'callStateReady':
            if 'on_call_ready' in self.call_handlers:
                await self.call_handlers['on_call_ready'](call)
        elif state == 'callStateDiscarded':
            if 'on_call_ended' in self.call_handlers:
                await self.call_handlers['on_call_ended'](call)
    
    async def _send(self, query: Dict[str, Any]):
        """Send query to TDLib"""
        query_str = json.dumps(query).encode('utf-8')
        self.tdjson.td_json_client_send(self.client, query_str)
    
    def register_handler(self, event: str, handler: Callable):
        """Register event handler"""
        self.call_handlers[event] = handler
    
    async def accept_call(self, call_id: int):
        """Accept incoming call"""
        await self._send({
            '@type': 'acceptCall',
            'call_id': call_id,
            'protocol': {
                '@type': 'callProtocol',
                'udp_p2p': True,
                'udp_reflector': True,
                'min_layer': 65,
                'max_layer': 92
            }
        })
    
    async def close(self):
        """Close TDLib client"""
        self._running = False
        self.auth_handler = AuthHandler()
        if self.client:
            await self._send({'@type': 'close'})
            await asyncio.sleep(1)
            self.tdjson.td_json_client_destroy(self.client)
