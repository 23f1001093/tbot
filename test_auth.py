#!/usr/bin/env python3
"""
Simple authentication test
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from ctypes import CDLL, c_void_p, c_char_p, c_double

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
            return p
    raise FileNotFoundError("TDLib not found")

async def test_auth():
    """Test authentication flow"""
    
    # Load TDLib
    tdlib = CDLL(find_tdlib())
    tdlib.td_json_client_create.restype = c_void_p
    tdlib.td_json_client_send.argtypes = [c_void_p, c_char_p]
    tdlib.td_json_client_receive.restype = c_char_p
    tdlib.td_json_client_receive.argtypes = [c_void_p, c_double]
    
    # Create client
    client = tdlib.td_json_client_create()
    
    # Load credentials
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE_NUMBER')
    
    print(f"Testing with phone: {phone[:3]}***{phone[-4:]}")
    
    # Send function
    def send(query):
        query_str = json.dumps(query).encode('utf-8')
        tdlib.td_json_client_send(client, query_str)
    
    # Receive function
    def receive(timeout=1.0):
        result = tdlib.td_json_client_receive(client, c_double(timeout))
        if result:
            return json.loads(result.decode('utf-8'))
        return None
    
    # Authentication flow
    auth_state = None
    code_sent = False
    
    while True:
        update = receive(1.0)
        
        if update:
            update_type = update.get('@type')
            
            if update_type == 'updateAuthorizationState':
                auth_state = update['authorization_state']['@type']
                print(f"Auth state: {auth_state}")
                
                if auth_state == 'authorizationStateWaitTdlibParameters':
                    # Send parameters
                    send({
                        '@type': 'setTdlibParameters',
                        'parameters': {
                            'use_test_dc': False,
                            'database_directory': './data/tdlib/db',
                            'files_directory': './data/tdlib/files',
                            'use_file_database': True,
                            'use_chat_info_database': True,
                            'use_message_database': True,
                            'use_secret_chats': False,
                            'api_id': api_id,
                            'api_hash': api_hash,
                            'system_language_code': 'en',
                            'device_model': 'Desktop',
                            'system_version': 'Unknown',
                            'application_version': '1.0'
                        }
                    })
                    
                elif auth_state == 'authorizationStateWaitEncryptionKey':
                    # Send empty encryption key
                    send({
                        '@type': 'checkDatabaseEncryptionKey',
                        'encryption_key': ''
                    })
                    
                elif auth_state == 'authorizationStateWaitPhoneNumber':
                    # Send phone number
                    print(f"Sending phone number: {phone}")
                    send({
                        '@type': 'setAuthenticationPhoneNumber',
                        'phone_number': phone,
                        'settings': {
                            '@type': 'phoneNumberAuthenticationSettings',
                            'allow_flash_call': False,
                            'allow_missed_call': False,
                            'is_current_phone_number': False,
                            'allow_sms_retriever_api': False
                        }
                    })
                    
                elif auth_state == 'authorizationStateWaitCode' and not code_sent:
                    # Request code from user
                    print("\n" + "="*50)
                    print("📲 CHECK YOUR TELEGRAM APP FOR THE CODE")
                    print("="*50)
                    code = input("Enter verification code: ").strip()
                    
                    send({
                        '@type': 'checkAuthenticationCode',
                        'code': code
                    })
                    code_sent = True
                    
                elif auth_state == 'authorizationStateWaitPassword':
                    # Request 2FA password
                    import getpass
                    password = getpass.getpass("Enter 2FA password: ")
                    
                    send({
                        '@type': 'checkAuthenticationPassword',
                        'password': password
                    })
                    
                elif auth_state == 'authorizationStateReady':
                    print("\n✅ SUCCESSFULLY LOGGED IN!")
                    break
                    
            elif update_type == 'error':
                print(f"Error: {update.get('message')}")
        
        await asyncio.sleep(0.01)
    
    # Cleanup
    send({'@type': 'close'})
    print("\nAuthentication test complete!")

if __name__ == "__main__":
    asyncio.run(test_auth())
