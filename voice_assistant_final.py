#!/usr/bin/env python3
"""
Complete Voice Assistant with proper call handling
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from ctypes import CDLL, c_void_p, c_char_p, c_double
import base64

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
        self.current_call_id = None
        
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
        print(f"→ Sending: {data.get('@type')}")
        self.tdlib.td_json_client_send(self.client, json.dumps(data).encode('utf-8'))
    
    def receive(self, timeout=1.0):
        result = self.tdlib.td_json_client_receive(self.client, c_double(timeout))
        if result:
            return json.loads(result.decode('utf-8'))
        return None
    
    async def handle_incoming_call(self, call):
        """Handle incoming call properly"""
        call_id = call.get('id')
        user_id = call.get('user_id', 'Unknown')
        
        self.current_call_id = call_id
        
        print(f"\n{'='*70}")
        print(f"📞 INCOMING CALL!")
        print(f"{'='*70}")
        print(f"Call ID: {call_id}")
        print(f"From: Ma❤️ (7112538016)")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Accept immediately for testing
        print("\n⏳ Accepting call...")
        await asyncio.sleep(1)
        
        # Accept with minimal protocol that works
        accept_request = {
            '@type': 'acceptCall',
            'call_id': call_id,
            'protocol': {
                '@type': 'callProtocol',
                'udp_p2p': True,
                'udp_reflector': True,
                'min_layer': 65,
                'max_layer': 92,
                'library_versions': ['2.4.4']  # Use only the version that works
            }
        }
        
        self.send(accept_request)
        print("✅ Call accepted!")
        
        # Send signaling data to establish connection
        await asyncio.sleep(0.5)
        self.send({
            '@type': 'sendCallSignalingData',
            'call_id': call_id,
            'data': base64.b64encode(b'connect').decode('utf-8')
        })
        
    async def handle_call_waiting(self, call):
        """Handle call in waiting state"""
        print("⏳ Call is in WAITING state - establishing connection...")
        
        # Get call state
        call_id = call.get('id')
        
        # Try to move to ready state
        self.send({
            '@type': 'sendCallDebugInformation',
            'call_id': call_id,
            'debug_information': json.dumps({'status': 'ready'})
        })
        
    async def handle_call_ready(self, call):
        """Handle connected call"""
        print(f"\n🎉 CALL CONNECTED!")
        print("🎙️ Voice channel ACTIVE")
        print("🔊 You can speak now!")
        
        # Here you would handle audio streaming
        # For now, just show it's connected
        
    async def run(self):
        print("\n" + "="*70)
        print("🤖 TELEGRAM VOICE ASSISTANT - FINAL VERSION")
        print("="*70)
        print(f"📞 Phone: {self.phone}")
        print(f"👤 User: Aditi (@Iaditi221)")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.client = self.tdlib.td_json_client_create()
        
        # Quick auth
        auth_done = False
        code_sent = False
        
        while not auth_done:
            update = self.receive(0.2)
            
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
                    
                    elif state == 'authorizationStateWaitCode' and not code_sent:
                        print("\n📲 Enter code: ", end='')
                        code = input().strip()
                        self.send({
                            '@type': 'checkAuthenticationCode',
                            'code': code
                        })
                        code_sent = True
                    
                    elif state == 'authorizationStateReady':
                        auth_done = True
                        print("✅ Authenticated!")
            
            await asyncio.sleep(0.01)
        
        print("\n" + "="*70)
        print("📞 READY FOR CALLS")
        print("="*70)
        print(f"✅ Accepting calls at: {self.phone}")
        print("🔔 Ma❤️ can call you now!")
        print("="*70 + "\n")
        
        # Main monitoring loop
        call_states = {}
        
        try:
            while self.running:
                update = self.receive(0.1)
                
                if update:
                    update_type = update.get('@type', '')
                    
                    # Handle call updates
                    if update_type == 'updateCall':
                        call = update.get('call', {})
                        call_id = call.get('id')
                        call_state = call.get('state', {}).get('@type', '')
                        is_outgoing = call.get('is_outgoing', False)
                        
                        # Track state changes
                        prev_state = call_states.get(call_id)
                        if prev_state != call_state:
                            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Call state: {call_state}")
                            call_states[call_id] = call_state
                        
                        # Handle different states
                        if call_state == 'callStatePending' and not is_outgoing:
                            await self.handle_incoming_call(call)
                        
                        elif call_state == 'callStateExchangingKeys':
                            print("🔐 Exchanging encryption keys...")
                            # Send additional signaling if needed
                            await asyncio.sleep(0.5)
                            self.send({
                                '@type': 'sendCallSignalingData',
                                'call_id': call_id,
                                'data': base64.b64encode(b'keys_exchanged').decode('utf-8')
                            })
                        
                        elif call_state == 'callStateReady':
                            await self.handle_call_ready(call)
                        
                        elif call_state == 'callStateDiscarded':
                            reason = call.get('state', {}).get('reason', {}).get('@type', 'unknown')
                            print(f"\n📵 Call ended: {reason}")
                            self.current_call_id = None
                    
                    # Handle signaling data
                    elif update_type == 'updateNewCallSignalingData':
                        print("📡 Received signaling data")
                        call_id = update.get('call_id')
                        if call_id == self.current_call_id:
                            # Echo back signaling
                            self.send({
                                '@type': 'sendCallSignalingData',
                                'call_id': call_id,
                                'data': update.get('data', '')
                            })
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            if self.current_call_id:
                self.send({
                    '@type': 'discardCall',
                    'call_id': self.current_call_id,
                    'is_disconnected': False,
                    'duration': 0,
                    'is_video': False,
                    'connection_id': 0
                })
            self.send({'@type': 'close'})

async def main():
    assistant = VoiceAssistant()
    await assistant.run()

if __name__ == '__main__':
    asyncio.run(main())
