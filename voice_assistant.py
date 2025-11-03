#!/usr/bin/env python3
"""
Telegram Voice Assistant - Ready to receive calls
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
    """Telegram Voice Assistant"""
    
    def __init__(self):
        # Load credentials
        self.api_id = int(os.getenv('TELEGRAM_API_ID'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE_NUMBER')
        
        # Find TDLib
        self.tdlib_path = self._find_tdlib()
        self.tdlib = CDLL(self.tdlib_path)
        self._setup_tdlib()
        
        self.client = None
        self.running = True
        
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
    
    async def handle_call(self, call):
        """Handle incoming/outgoing calls"""
        call_id = call['id']
        state = call['state']['@type']
        is_outgoing = call.get('is_outgoing', False)
        user_id = call.get('user_id')
        
        print(f"\n{'='*60}")
        print(f"📞 CALL EVENT")
        print(f"{'='*60}")
        print(f"Call ID: {call_id}")
        print(f"State: {state}")
        print(f"Direction: {'Outgoing' if is_outgoing else 'Incoming'}")
        print(f"User ID: {user_id}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        
        if state == 'callStatePending' and not is_outgoing:
            print("🔔 INCOMING CALL - Auto-answering in 2 seconds...")
            await asyncio.sleep(2)
            
            # Accept the call
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
            print("🎙️ CALL CONNECTED - Voice channel open")
            print("   [AI Voice Assistant would speak here]")
            
            # Here you would:
            # 1. Start receiving audio
            # 2. Convert speech to text
            # 3. Generate AI response
            # 4. Convert response to speech
            # 5. Send audio back
            
        elif state == 'callStateDiscarded':
            reason = call['state'].get('reason', {}).get('@type', 'unknown')
            print(f"📵 CALL ENDED - Reason: {reason}")
            print(f"{'='*60}\n")
    
    async def run(self):
        """Main run loop"""
        print("\n" + "="*60)
        print("🤖 TELEGRAM VOICE ASSISTANT")
        print("="*60)
        print(f"Phone: {self.phone}")
        print("Status: ACTIVE")
        print("-"*60)
        print("📞 READY TO RECEIVE CALLS")
        print("   • Incoming calls will be auto-answered")
        print("   • AI responses will be generated")
        print("   • Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        # Create client
        self.client = self.tdlib.td_json_client_create()
        
        # Already authenticated from your previous run
        # Just monitor for calls
        
        try:
            while self.running:
                update = self.receive(1.0)
                
                if update:
                    update_type = update.get('@type', '')
                    
                    # Handle different updates
                    if update_type == 'updateCall':
                        await self.handle_call(update['call'])
                        
                    elif update_type == 'updateNewMessage':
                        message = update['message']
                        if message.get('content', {}).get('@type') == 'messageText':
                            text = message['content'].get('text', {}).get('text', '')
                            sender = message.get('sender_id', {}).get('user_id', 'Unknown')
                            print(f"💬 Message from {sender}: {text[:50]}...")
                            
                    elif update_type == 'updateAuthorizationState':
                        state = update['authorization_state']['@type']
                        if state == 'authorizationStateClosed':
                            print("Session closed")
                            break
                        elif state == 'authorizationStateReady':
                            print("✅ Session active")
                    
                    elif update_type == 'error':
                        print(f"Error: {update.get('message')}")
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
        finally:
            self.running = False
            self.send({'@type': 'close'})
            await asyncio.sleep(1)
            self.tdlib.td_json_client_destroy(self.client)
            print("✅ Shutdown complete")

async def main():
    """Main entry point"""
    assistant = VoiceAssistant()
    await assistant.run()

if __name__ == '__main__':
    print("Starting Voice Assistant...")
    asyncio.run(main())
