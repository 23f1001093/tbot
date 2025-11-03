#!/usr/bin/env python3
"""
Working Telegram Voice Assistant - Updated for 2025
Fixes call rejection issue
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
        """Handle incoming call with proper protocol"""
        call_id = call.get('id')
        user_id = call.get('user_id', 'Unknown')
        
        print(f"\n{'='*70}")
        print(f"📞 INCOMING CALL DETECTED!")
        print(f"{'='*70}")
        print(f"Call ID: {call_id}")
        print(f"From User: {user_id}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Wait before answering (human-like behavior)
        print("\n⏳ Waiting 2 seconds before answering...")
        await asyncio.sleep(2)
        
        # CRITICAL: Use the correct protocol for 2025
        accept_request = {
            '@type': 'acceptCall',
            'call_id': call_id,
            'protocol': {
                '@type': 'callProtocol',
                'udp_p2p': True,
                'udp_reflector': True,
                'min_layer': 65,
                'max_layer': 92,
                'library_versions': ['2.4.4', '2.7.7', '3.0.0', '4.0.0', '5.0.0']
            }
        }
        
        print("📤 Accepting call with updated protocol...")
        self.send(accept_request)
        print("✅ Accept command sent!")
        
        # Also try sending call rating (sometimes helps)
        await asyncio.sleep(1)
        
        # Send ready signal
        self.send({
            '@type': 'sendCallSignalingData',
            'call_id': call_id,
            'data': b'ready'.hex()
        })
        
    async def run(self):
        print("\n" + "="*70)
        print("🤖 TELEGRAM VOICE ASSISTANT v2025")
        print("="*70)
        print(f"📞 Phone: {self.phone}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.client = self.tdlib.td_json_client_create()
        
        # Quick auth
        auth_done = False
        code_sent = False
        
        while not auth_done:
            update = self.receive(0.5)
            
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
                            'use_secret_chats': True,  # Changed to True
                            'system_language_code': 'en',
                            'device_model': 'Desktop',
                            'system_version': 'macOS',  # More specific
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
                        print("✅ Ready!")
                
                elif update_type == 'error':
                    print(f"Error: {update.get('message')}")
            
            await asyncio.sleep(0.01)
        
        # Set call options
        self.send({
            '@type': 'setOption',
            'name': 'use_pfs',
            'value': {'@type': 'optionValueBoolean', 'value': True}
        })
        
        print("\n" + "="*70)
        print("📞 MONITORING FOR CALLS - FIXED VERSION")
        print("="*70)
        print(f"✅ Phone: {self.phone}")
        print("🔔 Will auto-answer incoming calls")
        print("\n💡 Call from another account to test!")
        print("="*70 + "\n")
        
        # Main loop
        try:
            while self.running:
                update = self.receive(0.1)
                
                if update:
                    update_type = update.get('@type', '')
                    
                    # Debug: Show all updates
                    if 'call' in update_type.lower():
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {update_type}")
                    
                    # Handle call updates
                    if update_type == 'updateCall':
                        call = update.get('call', {})
                        call_state = call.get('state', {}).get('@type', '')
                        is_outgoing = call.get('is_outgoing', False)
                        
                        print(f"Call State: {call_state}, Outgoing: {is_outgoing}")
                        
                        # Handle different states
                        if call_state == 'callStatePending' and not is_outgoing:
                            await self.handle_incoming_call(call)
                        
                        elif call_state == 'callStateExchangingKeys':
                            print("🔐 Exchanging encryption keys...")
                        
                        elif call_state == 'callStateReady':
                            print("\n🎉 CALL CONNECTED SUCCESSFULLY!")
                            print("🎙️ Voice channel is ACTIVE")
                            print("🗣️ You can speak now!")
                        
                        elif call_state == 'callStateDiscarded':
                            reason = call.get('state', {}).get('reason', {}).get('@type', 'unknown')
                            print(f"\n📵 Call ended: {reason}")
                            
                            # Debug why call was discarded
                            if reason == 'callDiscardReasonDeclined':
                                print("❌ Call was declined (check protocol)")
                            elif reason == 'callDiscardReasonDisconnected':
                                print("❌ Call disconnected")
                            elif reason == 'callDiscardReasonHungUp':
                                print("📵 Other party hung up")
                            elif reason == 'callDiscardReasonMissed':
                                print("📵 Call was missed")
                        
                        elif call_state == 'callStateError':
                            error = call.get('state', {}).get('error', {})
                            print(f"❌ Call error: {error}")
                    
                    # Handle call signaling
                    elif update_type == 'updateNewCallSignalingData':
                        print("📡 Received call signaling data")
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.send({'@type': 'close'})

async def main():
    assistant = VoiceAssistant()
    await assistant.run()

if __name__ == '__main__':
    asyncio.run(main())
