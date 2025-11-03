#!/usr/bin/env python3
"""
Working TDLib authentication with correct parameter structure
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from ctypes import CDLL, c_void_p, c_char_p, c_double

# Load environment
load_dotenv()

def find_tdlib():
    """Find TDLib library"""
    paths = [
        './tdlib/lib/libtdjson.dylib',
        './tdlib/build/libtdjson.dylib',
        './tdlib/lib/libtdjson.so',
        './tdlib/build/libtdjson.so'
    ]
    for p in paths:
        if Path(p).exists():
            print(f"Found TDLib at: {p}")
            return p
    raise FileNotFoundError("TDLib library not found")

async def main():
    """Main authentication flow"""
    
    # Load and verify credentials
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE_NUMBER')
    
    print("="*60)
    print("🚀 TDLib Authentication Test")
    print("="*60)
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash[:8]}...")
    print(f"Phone: {phone[:6]}****")
    print("-"*60)
    
    # Create data directories
    Path('./data/tdlib/db').mkdir(parents=True, exist_ok=True)
    Path('./data/tdlib/files').mkdir(parents=True, exist_ok=True)
    
    # Load TDLib
    tdlib_path = find_tdlib()
    tdlib = CDLL(tdlib_path)
    
    # Setup functions
    tdlib.td_json_client_create.restype = c_void_p
    tdlib.td_json_client_send.argtypes = [c_void_p, c_char_p]
    tdlib.td_json_client_receive.restype = c_char_p
    tdlib.td_json_client_receive.argtypes = [c_void_p, c_double]
    tdlib.td_json_client_destroy.argtypes = [c_void_p]
    
    # Create client
    client = tdlib.td_json_client_create()
    print("✅ TDLib client created")
    
    def send(data):
        """Send request to TDLib"""
        request = json.dumps(data)
        print(f"→ Sending: {data.get('@type')}")
        tdlib.td_json_client_send(client, request.encode('utf-8'))
    
    def receive(timeout=2.0):
        """Receive response from TDLib"""
        result = tdlib.td_json_client_receive(client, c_double(timeout))
        if result:
            return json.loads(result.decode('utf-8'))
        return None
    
    # State tracking
    code_requested = False
    password_requested = False
    
    print("\n🔄 Starting authentication flow...")
    print("-"*60)
    
    while True:
        # Receive update
        update = receive(1.0)
        
        if update:
            update_type = update.get('@type', '')
            
            if update_type == 'updateAuthorizationState':
                state = update['authorization_state']['@type']
                print(f"📍 State: {state}")
                
                if state == 'authorizationStateWaitTdlibParameters':
                    # Send TDLib parameters - CRITICAL PART
                    params = {
                        '@type': 'setTdlibParameters',
                        'api_id': api_id,
                        'api_hash': api_hash,
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
                    send(params)
                
                elif state == 'authorizationStateWaitPhoneNumber':
                    # Send phone number
                    print(f"📱 Sending phone number: {phone}")
                    send({
                        '@type': 'setAuthenticationPhoneNumber',
                        'phone_number': phone,
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
                    # Request verification code
                    print("\n" + "="*60)
                    print("📲 VERIFICATION REQUIRED")
                    print("="*60)
                    print("Check your Telegram app for a code from:")
                    print("  • Telegram official account")
                    print("  • SMS to your phone")
                    print("-"*60)
                    
                    code = input("Enter verification code (5 digits): ").strip()
                    
                    send({
                        '@type': 'checkAuthenticationCode',
                        'code': code
                    })
                    code_requested = True
                
                elif state == 'authorizationStateWaitPassword' and not password_requested:
                    # Request 2FA password
                    print("\n🔐 2FA Password Required")
                    import getpass
                    password = getpass.getpass("Enter password: ")
                    
                    send({
                        '@type': 'checkAuthenticationPassword',
                        'password': password
                    })
                    password_requested = True
                
                elif state == 'authorizationStateReady':
                    print("\n" + "="*60)
                    print("✅ SUCCESSFULLY LOGGED IN!")
                    print("="*60)
                    print("\n📞 Ready to receive calls")
                    print("Press Ctrl+C to exit\n")
                    break
                
                elif state == 'authorizationStateClosed':
                    print("Session closed")
                    return
            
            elif update_type == 'error':
                print(f"❌ Error: {update['message']}")
                print(f"Code: {update.get('code')}")
                
                # If parameters error, show what we're sending
                if 'api_id' in update.get('message', ''):
                    print(f"\nDebug: We're sending api_id={api_id} (type: {type(api_id)})")
                    print(f"Debug: We're sending api_hash={api_hash[:8]}... (type: {type(api_hash)})")
            
            elif update_type == 'updateCall':
                call = update['call']
                print(f"\n📞 CALL UPDATE: {call['state']['@type']}")
                if call['state']['@type'] == 'callStatePending':
                    print(f"   From user: {call.get('user_id')}")
    
    # Keep running to monitor for calls
    try:
        while True:
            update = receive(1.0)
            if update:
                if update.get('@type') == 'updateCall':
                    print(f"📞 Call event: {update}")
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    
    # Cleanup
    send({'@type': 'close'})
    tdlib.td_json_client_destroy(client)
    print("✅ Clean shutdown complete")

if __name__ == '__main__':
    asyncio.run(main())
