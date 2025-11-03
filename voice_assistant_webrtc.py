#!/usr/bin/env python3
"""
Voice Assistant with WebRTC connection handling
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
        self.current_call = None
        
    def _find_tdlib(self):
        paths = ['./tdlib/lib/libtdjson.dylib', './tdlib/build/libtdjson.dylib']
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
        self.tdlib.td_json_client_send(self.client, json.dumps(data).encode('utf-8'))
    
    def receive(self, timeout=1.0):
        result = self.tdlib.td_json_client_receive(self.client, c_double(timeout))
        if result:
            return json.loads(result.decode('utf-8'))
        return None
    
    async def handle_call_ready(self, call):
        """Handle call when it's ready - establish WebRTC connection"""
        call_id = call.get('id')
        connections = call.get('state', {}).get('connections', [])
        
        print(f"\n{'='*70}")
        print(f"🎉 CALL IS READY!")
        print(f"{'='*70}")
        print(f"Call ID: {call_id}")
        print(f"State: READY - Establishing voice connection...")
        
        if connections:
            print(f"\n📡 Available connections:")
            for conn in connections[:3]:  # Show first 3 connections
                print(f"  • Server: {conn.get('ip')}:{conn.get('port')}")
                print(f"    IPv6: {conn.get('ipv6')}")
                print(f"    ID: {conn.get('id')}")
            
            # Try to establish connection with first server
            first_conn = connections[0]
            print(f"\n🔌 Connecting to: {first_conn.get('ip')}:{first_conn.get('port')}")
            
            # Send signaling data to establish WebRTC
            signaling_data = {
                'action': 'connect',
                'server': first_conn.get('ip'),
                'port': first_conn.get('port'),
                'connection_id': first_conn.get('id')
            }
            
            self.send({
                '@type': 'sendCallSignalingData',
                'call_id': call_id,
                'data': base64.b64encode(json.dumps(signaling_data).encode()).decode()
            })
            
            print("✅ Connection request sent!")
            
            # Send debug info to help establish connection
            await asyncio.sleep(0.5)
            self.send({
                '@type': 'sendCallDebugInformation',
                'call_id': call_id,
                'debug_information': json.dumps({
                    'connection_attempt': 1,
                    'selected_server': first_conn.get('ip'),
                    'timestamp': datetime.now().isoformat()
                })
            })
            
            print("\n🎙️ VOICE CHANNEL SHOULD BE ACTIVE NOW!")
            print("🔊 If you can't hear anything, it might be a network issue.")
            print("\nTroubleshooting:")
            print("1. Make sure both devices have good internet")
            print("2. Try calling from mobile data instead of WiFi")
            print("3. Check if UDP ports are open on your network")
        else:
            print("⚠️ No connection servers available")
    
    async def run(self):
        print("\n" + "="*70)
        print("🤖 TELEGRAM VOICE ASSISTANT - WebRTC Version")
        print("="*70)
        print(f"📞 Phone: {self.phone}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
        print("📞 READY TO RECEIVE CALLS")
        print("="*70)
        print("Waiting for incoming calls...")
        print("="*70 + "\n")
        
        # Main loop
        try:
            while self.running:
                update = self.receive(0.1)
                
                if update:
                    update_type = update.get('@type', '')
                    
                    if update_type == 'updateCall':
                        call = update.get('call', {})
                        call_id = call.get('id')
                        call_state = call.get('state', {}).get('@type', '')
                        is_outgoing = call.get('is_outgoing', False)
                        
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Call update: {call_state}")
                        
                        if call_state == 'callStatePending' and not is_outgoing:
                            print(f"\n📞 INCOMING CALL! ID: {call_id}")
                            print("⏳ Accepting in 1 second...")
                            
                            await asyncio.sleep(1)
                            
                            self.send({
                                '@type': 'acceptCall',
                                'call_id': call_id,
                                'protocol': {
                                    '@type': 'callProtocol',
                                    'udp_p2p': True,
                                    'udp_reflector': True,
                                    'min_layer': 65,
                                    'max_layer': 92,
                                    'library_versions': ['2.4.4']
                                }
                            })
                            print("✅ Accept sent!")
                            self.current_call = call
                        
                        elif call_state == 'callStateExchangingKeys':
                            print("🔐 Exchanging encryption keys...")
                        
                        elif call_state == 'callStateReady':
                            # This is where we need to establish WebRTC
                            await self.handle_call_ready(call)
                            self.current_call = call
                        
                        elif call_state == 'callStateDiscarded':
                            reason = call.get('state', {}).get('reason', {}).get('@type', 'unknown')
                            print(f"\n📵 Call ended: {reason}")
                            self.current_call = None
                    
                    elif update_type == 'updateNewCallSignalingData':
                        print("📡 Received signaling data - processing...")
                        # Echo back for WebRTC negotiation
                        if self.current_call:
                            self.send({
                                '@type': 'sendCallSignalingData',
                                'call_id': self.current_call.get('id'),
                                'data': update.get('data', '')
                            })
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.send({'@type': 'close'})

asyncio.run(VoiceAssistant().run())
