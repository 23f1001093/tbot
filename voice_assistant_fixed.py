#!/usr/bin/env python3
"""
Fixed Telegram Voice Assistant - Properly handles incoming calls
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from ctypes import CDLL, c_void_p, c_char_p, c_double

load_dotenv()

class VoiceAssistant:
    def __init__(self):
        self.api_id = int(os.getenv('TELEGRAM_API_ID'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE_NUMBER')
        
        Path('./data/tdlib/db').mkdir(parents=True, exist_ok=True)
        Path('./data/tdlib/files').mkdir(parents=True, exist_ok=True)
        
        self.tdlib_path = self._find_tdlib()
        self.tdlib = CDLL(self.tdlib_path)
        self._setup_tdlib()
        
        self.client = None
        self.running = True
        self.authenticated = False
    
    def _find_tdlib(self):
        paths = [
            './tdlib/lib/libtdjson.dylib',
            './tdlib/build/libtdjson.dylib',
        ]
        for p in paths:
            if Path(p).exists():
                return p
        raise FileNotFoundError("TDLib not found")
    
    def _setup_tdlib(self):
        self.tdlib.td_json_client_create.restype = c_void_p
        self.tdlib.td_json_client_send.argtypes = [c_void_p, c_char_p]
        self.tdlib.td_json_client_receive.restype = c_char_p
        self.tdlib.td_json_client_receive.argtypes = [c_void_p, c_double]
    
    def send(self, data):
        if self.client:
            self.tdlib.td_json_client_send(self.client, json.dumps(data).encode('utf-8'))
    
    def receive(self, timeout=1.0):
        if self.client:
            result = self.tdlib.td_json_client_receive(self.client, c_double(timeout))
            if result:
                return json.loads(result.decode('utf-8'))
        return None
    
    async def run(self):
        print("\n" + "="*70)
        print("🤖 TELEGRAM VOICE ASSISTANT - CALL HANDLER")
        print("="*70)
        print(f"📞 Phone: {self.phone}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.client = self.tdlib.td_json_client_create()
        
        # Authentication
        print("\n🔐 Authenticating...")
        auth_complete = False
        code_requested = False
        
        while not auth_complete:
            update = self.receive(1.0)
            
            if update:
                update_type = update.get('@type', '')
                
                if update_type == 'updateAuthorizationState':
                    state = update['authorization_state']['@type']
                    
                    if state == 'authorizationStateWaitTdlibParameters':
                        self.send({
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
                        })
                    
                    elif state == 'authorizationStateWaitPhoneNumber':
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
                    
                    elif state == 'authorizationStateWaitCode' and not code_requested:
                        print("\n📲 Enter verification code from Telegram: ", end='')
                        code = input().strip()
                        self.send({
                            '@type': 'checkAuthenticationCode',
                            'code': code
                        })
                        code_requested = True
                    
                    elif state == 'authorizationStateWaitPassword':
                        import getpass
                        password = getpass.getpass("🔐 Enter 2FA password: ")
                        self.send({
                            '@type': 'checkAuthenticationPassword',
                            'password': password
                        })
                    
                    elif state == 'authorizationStateReady':
                        auth_complete = True
                        print("✅ Authenticated successfully!")
                
                elif update_type == 'error':
                    print(f"Error: {update.get('message')}")
            
            await asyncio.sleep(0.01)
        
        # Main monitoring loop
        print("\n" + "="*70)
        print("📞 MONITORING FOR INCOMING CALLS")
        print("="*70)
        print("✅ Ready to receive calls at: " + self.phone)
        print("🔔 Auto-answer is ENABLED")
        print("⏱️ Will answer after 2 seconds")
        print("\n💡 Test by calling from another Telegram account!")
        print("="*70 + "\n")
        
        call_count = 0
        last_update_time = datetime.now()
        
        try:
            while self.running:
                update = self.receive(0.1)
                
                if update:
                    update_type = update.get('@type', '')
                    current_time = datetime.now().strftime('%H:%M:%S')
                    
                    # LOG ALL UPDATES (for debugging)
                    if 'update' in update_type.lower():
                        if update_type not in ['updateOption', 'updateAuthorizationState', 'updateConnectionState']:
                            print(f"[{current_time}] 📡 {update_type}")
                    
                    # HANDLE CALLS
                    if update_type == 'updateCall':
                        call_count += 1
                        call = update.get('call', {})
                        call_id = call.get('id')
                        call_state = call.get('state', {}).get('@type', '')
                        is_outgoing = call.get('is_outgoing', False)
                        user_id = call.get('user_id', 'Unknown')
                        
                        print(f"\n{'='*70}")
                        print(f"🔔 CALL EVENT #{call_count} at {current_time}")
                        print(f"{'='*70}")
                        print(f"Call ID: {call_id}")
                        print(f"State: {call_state}")
                        print(f"Direction: {'Outgoing' if is_outgoing else 'INCOMING'}")
                        print(f"User ID: {user_id}")
                        
                        # HANDLE INCOMING CALL
                        if call_state == 'callStatePending' and not is_outgoing:
                            print(f"\n🎉 INCOMING CALL DETECTED!")
                            print(f"📞 From User: {user_id}")
                            print(f"⏰ Time: {current_time}")
                            print(f"🔔 Auto-answering in 2 seconds...")
                            
                            await asyncio.sleep(2)
                            
                            # ACCEPT THE CALL
                            accept_request = {
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
                            }
                            
                            print(f"📤 Sending accept call request...")
                            self.send(accept_request)
                            print(f"✅ CALL ACCEPTED!")
                        
                        elif call_state == 'callStateExchangingKeys':
                            print("🔐 Exchanging encryption keys...")
                        
                        elif call_state == 'callStateReady':
                            print(f"\n🎙️ CALL CONNECTED!")
                            print(f"📢 Voice channel is OPEN")
                            print(f"🤖 AI Assistant is ready to speak")
                        
                        elif call_state == 'callStateHangingUp':
                            print("📵 Call hanging up...")
                        
                        elif call_state == 'callStateDiscarded':
                            print(f"📵 CALL ENDED")
                            duration = call.get('duration', 0)
                            if duration > 0:
                                print(f"⏱️ Duration: {duration} seconds")
                            print(f"{'='*70}\n")
                        
                        elif call_state == 'callStateError':
                            error = call.get('state', {}).get('error', {})
                            print(f"❌ Call error: {error.get('message', 'Unknown error')}")
                    
                    # Show we're alive every 30 seconds
                    if (datetime.now() - last_update_time).seconds > 30:
                        print(f"[{current_time}] 💚 Assistant is active and monitoring...")
                        last_update_time = datetime.now()
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Stopping assistant...")
        finally:
            self.running = False
            self.send({'@type': 'close'})
            print("✅ Assistant stopped")

async def main():
    assistant = VoiceAssistant()
    await assistant.run()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
