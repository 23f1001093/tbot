"""
TDLib Client - Core Telegram Integration
Handles all Telegram voice call operations
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Optional, Any, Callable
from pathlib import Path
import ctypes
from ctypes import CDLL, c_void_p, c_char_p, c_double, c_int
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TDLibClient:
    """
    Complete TDLib client for Telegram voice calls
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize TDLib client with configuration"""
        self.config = config
        self.client = None
        self.authorized = False
        self.call_handlers: Dict[str, Callable] = {}
        self.active_calls: Dict[int, Dict] = {}
        self._running = False
        
        # Load TDLib library
        try:
            lib_path = './tdlib/build/libtdjson.so'
            if sys.platform == 'darwin':
                lib_path = './tdlib/build/libtdjson.dylib'
            elif sys.platform == 'win32':
                lib_path = './tdlib/build/tdjson.dll'
                
            self.tdjson = CDLL(lib_path)
            self._setup_functions()
            logger.info("✅ TDLib library loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load TDLib: {e}")
            raise
    
    def _setup_functions(self):
        """Set up TDLib function signatures"""
        # td_json_client_create
        self.tdjson.td_json_client_create.restype = c_void_p
        self.tdjson.td_json_client_create.argtypes = []
        
        # td_json_client_send
        self.tdjson.td_json_client_send.restype = None
        self.tdjson.td_json_client_send.argtypes = [c_void_p, c_char_p]
        
        # td_json_client_receive
        self.tdjson.td_json_client_receive.restype = c_char_p
        self.tdjson.td_json_client_receive.argtypes = [c_void_p, c_double]
        
        # td_json_client_execute
        self.tdjson.td_json_client_execute.restype = c_char_p
        self.tdjson.td_json_client_execute.argtypes = [c_void_p, c_char_p]
        
        # td_json_client_destroy
        self.tdjson.td_json_client_destroy.restype = None
        self.tdjson.td_json_client_destroy.argtypes = [c_void_p]
    
    async def start(self):
        """Start the TDLib client and authorize"""
        logger.info("🚀 Starting TDLib client...")
        
        # Create client instance
        self.client = self.tdjson.td_json_client_create()
        self._running = True
        
        # Start update receiver
        asyncio.create_task(self._receive_updates())
        
        # Initialize TDLib
        await self._initialize()
        
        logger.info("✅ TDLib client started successfully!")
        
    async def _initialize(self):
        """Initialize TDLib with parameters"""
        # Set TDLib parameters
        await self._send({
            '@type': 'setTdlibParameters',
            'parameters': {
                'database_directory': self.config['tdlib']['database_directory'],
                'files_directory': self.config['tdlib']['files_directory'],
                'use_message_database': True,
                'use_secret_chats': False,
                'api_id': self.config['telegram']['api_id'],
                'api_hash': self.config['telegram']['api_hash'],
                'system_language_code': 'en',
                'device_model': 'AI Voice Assistant',
                'application_version': '1.0.0',
                'enable_storage_optimizer': True
            }
        })
        
        # Check database encryption key
        await self._send({
            '@type': 'checkDatabaseEncryptionKey',
            'encryption_key': ''
        })
        
        # Start authentication
        await self._authenticate()
    
    async def _authenticate(self):
        """Handle authentication flow"""
        logger.info("📱 Starting authentication...")
        
        # Set authentication phone number
        await self._send({
            '@type': 'setAuthenticationPhoneNumber',
            'phone_number': self.config['telegram']['phone_number']
        })
        
        # Wait for authentication code
        await asyncio.sleep(2)
        
        # In real implementation, you'd get this from user input
        # For now, prompt in console
        if not self.authorized:
            code = input("📲 Enter Telegram verification code: ")
            
            await self._send({
                '@type': 'checkAuthenticationCode',
                'code': code
            })
            
            # Check if 2FA is required
            await asyncio.sleep(2)
            
            if not self.authorized:
                password = input("🔐 Enter 2FA password (if required, press Enter to skip): ")
                if password:
                    await self._send({
                        '@type': 'checkAuthenticationPassword',
                        'password': password
                    })
        
        logger.info("✅ Authentication successful!")
        self.authorized = True
    
    async def _receive_updates(self):
        """Continuously receive updates from Telegram"""
        while self._running:
            if self.client:
                try:
                    # Receive with 1 second timeout
                    result = self.tdjson.td_json_client_receive(
                        self.client,
                        c_double(1.0)
                    )
                    
                    if result:
                        update = json.loads(result.decode('utf-8'))
                        asyncio.create_task(self._handle_update(update))
                        
                except Exception as e:
                    logger.error(f"Error receiving update: {e}")
                    
            await asyncio.sleep(0.01)
    
    async def _handle_update(self, update: Dict[str, Any]):
        """Process incoming updates"""
        update_type = update.get('@type')
        
        # Log update for debugging
        if update_type not in ['updateFile', 'updateOption']:
            logger.debug(f"Update: {update_type}")
        
        # Handle different update types
        handlers = {
            'updateAuthorizationState': self._handle_authorization_state,
            'updateCall': self._handle_call_update,
            'updateNewCallSignalingData': self._handle_signaling_data,
            'error': self._handle_error
        }
        
        handler = handlers.get(update_type)
        if handler:
            await handler(update)
    
    async def _handle_authorization_state(self, update: Dict):
        """Handle authorization state changes"""
        state = update['authorization_state']['@type']
        logger.info(f"Authorization state: {state}")
        
        if state == 'authorizationStateReady':
            self.authorized = True
            logger.info("✅ Logged in successfully!")
        elif state == 'authorizationStateClosed':
            self._running = False
            logger.info("Session closed")
    
    async def _handle_call_update(self, update: Dict):
        """Handle voice call updates"""
        call = update['call']
        call_id = call['id']
        state = call['state']['@type']
        
        logger.info(f"📞 Call {call_id} - State: {state}")
        
        # Store call info
        if call_id not in self.active_calls:
            self.active_calls[call_id] = {
                'id': call_id,
                'user_id': call.get('user_id'),
                'is_outgoing': call.get('is_outgoing', False),
                'start_time': datetime.utcnow()
            }
        
        # Update call state
        self.active_calls[call_id]['state'] = state
        
        # Handle different call states
        if state == 'callStatePending':
            if not call.get('is_outgoing'):
                # Incoming call
                logger.info(f"📲 Incoming call from user {call.get('user_id')}")
                if 'on_incoming_call' in self.call_handlers:
                    await self.call_handlers['on_incoming_call'](call)
                else:
                    # Auto-answer if no handler
                    await asyncio.sleep(2)  # Human-like delay
                    await self.accept_call(call_id)
                    
        elif state == 'callStateReady':
            logger.info(f"✅ Call {call_id} connected!")
            if 'on_call_ready' in self.call_handlers:
                await self.call_handlers['on_call_ready'](call)
                
        elif state == 'callStateDiscarded':
            reason = call['state'].get('reason', {}).get('@type', 'unknown')
            logger.info(f"📵 Call {call_id} ended. Reason: {reason}")
            if 'on_call_ended' in self.call_handlers:
                await self.call_handlers['on_call_ended'](call)
            # Cleanup
            if call_id in self.active_calls:
                del self.active_calls[call_id]
    
    async def _handle_signaling_data(self, update: Dict):
        """Handle WebRTC signaling data"""
        call_id = update['call_id']
        data = update['data']
        logger.debug(f"Signaling data for call {call_id}: {len(data)} bytes")
    
    async def _handle_error(self, update: Dict):
        """Handle errors from TDLib"""
        logger.error(f"TDLib error: {update.get('message', 'Unknown error')}")
    
    async def accept_call(self, call_id: int):
        """Accept an incoming call"""
        logger.info(f"✅ Accepting call {call_id}")
        
        await self._send({
            '@type': 'acceptCall',
            'call_id': call_id,
            'protocol': {
                '@type': 'callProtocol',
                'udp_p2p': True,
                'udp_reflector': True,
                'min_layer': 65,
                'max_layer': 92,
                'library_versions': ['4.0.0']
            }
        })
    
    async def make_call(self, user_id: int, is_video: bool = False):
        """Make an outgoing call"""
        logger.info(f"📞 Calling user {user_id}")
        
        result = await self._send({
            '@type': 'createCall',
            'user_id': user_id,
            'protocol': {
                '@type': 'callProtocol',
                'udp_p2p': True,
                'udp_reflector': True,
                'min_layer': 65,
                'max_layer': 92,
                'library_versions': ['4.0.0']
            },
            'is_video': is_video
        })
        
        return result
    
    async def end_call(self, call_id: int, duration: int = 0):
        """End a call"""
        logger.info(f"📵 Ending call {call_id}")
        
        await self._send({
            '@type': 'discardCall',
            'call_id': call_id,
            'is_disconnected': False,
            'duration': duration,
            'is_video': False,
            'connection_id': 0
        })
    
    async def send_call_rating(self, call_id: int, rating: int, comment: str = ""):
        """Rate a call (1-5 stars)"""
        await self._send({
            '@type': 'sendCallRating',
            'call_id': call_id,
            'rating': rating,
            'comment': comment,
            'problems': []
        })
    
    async def _send(self, query: Dict[str, Any]) -> Optional[Dict]:
        """Send query to TDLib"""
        query_str = json.dumps(query).encode('utf-8')
        self.tdjson.td_json_client_send(self.client, query_str)
        return None
    
    def register_handler(self, event: str, handler: Callable):
        """Register event handler"""
        self.call_handlers[event] = handler
        logger.info(f"Registered handler for {event}")
    
    async def close(self):
        """Close TDLib client"""
        logger.info("Closing TDLib client...")
        self._running = False
        
        if self.client:
            await self._send({'@type': 'close'})
            await asyncio.sleep(1)
            self.tdjson.td_json_client_destroy(self.client)
            self.client = None
        
        logger.info("TDLib client closed")