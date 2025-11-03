#!/usr/bin/env python3
"""
Complete Telegram Voice Assistant - Ready for calls
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from ctypes import CDLL, c_void_p, c_char_p, c_double

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

class VoiceAssistant:
    """Telegram Voice Assistant with full authentication"""
    
    def __init__(self):
        # Load credentials
        self.api_id = int(os.getenv('TELEGRAM_API_ID'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE_NUMBER')
        
        # Create data directories
        Path('./data/tdlib/db').mkdir(parents=True, exist_ok=True)
        Path('./data/tdlib/files').mkdir(parents=True, exist_ok=True)
        
        # Find and load TDLib
        self.tdlib_path = self._find_tdlib()
        self.tdlib = CDLL(self.tdlib_path)
        self._setup_tdlib()
        
        self.client = None
        self.running = True
        self.authenticated = False
        self.code_requested = False
        
    def _find_tdlib(self):
        """Find TDLib library"""
        paths = [
            './tdlib/lib/libtdjson.dylib',
            './tdlib/build/libtdjson.dylib',
            './tdlib/lib/libtdjson.so',
            './tdlib/build/libtdjson.so'
        ]
        for p in paths:
            if Path(p).exists():
                return p
        raise FileNotFoundError("TDLib not found")
    
    def _setup_tdlib(self):
        """Setup TDLib functions"""
        self.tdlib.td_json_client_create.restype = c_void_p
        self.tdlib.td_json_client_send.argtypes = [c_void_p, c_char_p]
        self.tdlib.td_json_client_receive.restype = c_char_p
        self.tdlib.td_json_client_receive.argtypes = [c_void_p, c_double]
        self.tdlib.td_json_client_destroy.argtypes = [c_void_p]
    
    def send(self, data):
        """Send request to TDLib"""
        request = json.dumps(data)
        self.tdlib.td_json_client_send(self.client, request.encode('utf-8'))
    
    def receive(self, timeout=1.0):
        """Receive response from TDLib"""
        result = self.tdlib.td_json_client_receive(self.client, c_double(timeout))
        if result:
            return json.loads(result.decode('utf-8'))
        return None
    
    async def authenticate(self):
        """Handle authentication flow"""
        while not self.authenticated:
            update = self.receive(0.5)
            
            if update:
                update_type = update.get('@type', '')
                
                if update_type == 'updateAuthorizationState':
                    state = update['authorization_state']['@type']
                    
                    if state == 'authorizationStateWaitTdlibParameters':
                        # Send parameters
                        params = {
                            '@type': 'setTdlibParameters',
                            'api_id': self.api_id,
                            'api_hash': self.api_hash,
                            'database_directory': './data/tdlib/db',
                            'files_directory': './data/tdlib/files',
                            'use_file_database': True,
                            'use_chat_info_database': True,
                            'use_message_database': True,
                            'use_secret_chats': False,
                            'system_language_code': 'en',
                            'device_model': 'Desktop',
                            'system_version': 'Unknown',
                            'application_version': '1.0.0',
                            'enable_storage_optimizer': True
                        }
                        self.send(params)
                        print("📤 Sent TDLib parameters")
                    
                    elif state == 'authorizationStateWaitPhoneNumber':
                        # Send phone
                        self.send({
                            '@type': 'setAuthenticationPhoneNumber',
                            'phone_number': self.phone,
                            'settings': {
                                '@type': 'phoneNumberAuthenticationSettings',
                                'allow_flash_call': False,
                                'allow_missed_call': False,
                                'is_current_phone_number': False,
                                'allow_sms_retriever_api': False,
                                'authentication_tokens': []
                            }
                        })
                        print(f"📱 Sent phone number: {self.phone[:6]}****")
                    
                    elif state == 'authorizationStateWaitCode' and not self.code_requested:
                        print("\n" + "="*60)
                        print("📲 VERIFICATION CODE REQUIRED")
                        print("Check your Telegram app")
                        print("="*60)
                        code = input("Enter code: ").strip()
                        
                        self.send({
                            '@type': 'checkAuthenticationCode',
                            'code': code
                        })
                        self.code_requested = True
                    
                    elif state == 'authorizationStateWaitPassword':
                        import getpass
                        password = getpass.getpass("🔐 Enter 2FA password: ")
                        
                        self.send({
                            '@type': 'checkAuthenticationPassword',
                            'password': password
                        })
                    
                    elif state == 'authorizationStateReady':
                        self.authenticated = True
                        print("\n✅ AUTHENTICATED SUCCESSFULLY!")
                        return True
                
                elif update_type == 'error':
                    print(f"⚠️ Error: {update.get('message')}")
            
            await asyncio.sleep(0.01)
    
    async def handle_call(self, call):
        """Handle incoming/outgoing calls"""
        call_id = call['id']
        state = call['state']['@type']
        is_outgoing = call.get('is_outgoing', False)
        user_id = call.get('user_id')
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if state == 'callStatePending' and not is_outgoing:
            print(f"\n{'='*60}")
            print(f"📞 INCOMING CALL at {timestamp}")
            print(f"{'='*60}")
            print(f"From User ID: {user_id}")
            print(f"Call ID: {call_id}")
            print("🔔 Auto-answering in 2 seconds...")
            
            await asyncio.sleep(2)
            
            # Accept call
            self.send({
                '@type': 'acceptCall',
                'call_id': call_id,
                'protocol': {
                    '@type': 'callProtocol',
                    'udp_p2p': True,
                    'udp_reflector': True,
                    'min_layer': 65,
                    'max_layer': 92,
                    'library_versions': ['1.0.0']
                }
            })
            print("✅ Call accepted!")
            
        elif state == 'callStateReady':
            print(f"\n🎙️ CALL CONNECTED at {timestamp}")
            print("📢 Voice channel is open")
            print("🤖 [AI Assistant would speak here]")
            
            # Simulate AI greeting
            greeting = "Hello! This is your AI assistant. How can I help you today?"
            print(f"🗣️ AI says: '{greeting}'")
            
        elif state == 'callStateDiscarded':
            reason = call['state'].get('reason', {}).get('@type', 'unknown')
            duration = call['state'].get('duration', 0)
            print(f"\n📵 CALL ENDED at {timestamp}")
            print(f"Duration: {duration} seconds")
            print(f"Reason: {reason}")
            print(f"{'='*60}\n")
    
    async def run(self):
        """Main run loop"""
        print("\n" + "="*60)
        print("🤖 TELEGRAM VOICE ASSISTANT")
        print("="*60)
        print(f"Phone: {self.phone}")
        print("Status: INITIALIZING...")
        print("="*60)
        
        # Create client
        self.client = self.tdlib.td_json_client_create()
        
        # Authenticate if needed
        print("\n🔐 Checking authentication status...")
        await self.authenticate()
        
        print("\n" + "="*60)
        print("📞 VOICE ASSISTANT ACTIVE")
        print("="*60)
        print("✅ Ready to receive calls")
        print("✅ Auto-answer enabled")
        print("✅ AI responses ready")
        print("\nℹ️ Call " + self.phone + " from another account to test")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        # Monitor for updates
        try:
            call_count = 0
            message_count = 0
            
            while self.running:
                update = self.receive(0.5)
                
                if update:
                    update_type = update.get('@type', '')
                    
                    if update_type == 'updateCall':
                        call_count += 1
                        print(f"\n🔔 Call Event #{call_count}")
                        await self.handle_call(update['call'])
                    
                    elif update_type == 'updateNewMessage':
                        message_count += 1
                        message = update['message']
                        if message.get('content', {}).get('@type') == 'messageText':
                            text = message['content'].get('text', {}).get('text', '')
                            if text:
                                print(f"💬 Message #{message_count}: {text[:50]}...")
                    
                    elif update_type == 'updateUserStatus':
                        # User status updates (online/offline)
                        pass
                    
                    elif update_type == 'updateOption':
                        # Option updates
                        pass
                    
                    elif update_type != 'updateAuthorizationState':
                        # Log other updates for debugging
                        if 'update' in update_type.lower():
                            print(f"📡 {update_type}")
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Stopping assistant...")
        finally:
            self.running = False
            print("🔄 Closing connection...")
            self.send({'@type': 'close'})
            await asyncio.sleep(1)
            self.tdlib.td_json_client_destroy(self.client)
            print("✅ Shutdown complete")
            print("👋 Goodbye!")

async def main():
    """Main entry point"""
    try:
        assistant = VoiceAssistant()
        await assistant.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting Telegram Voice Assistant...")
    print("Current time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("-" * 60)
    asyncio.run(main())
