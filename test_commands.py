#!/usr/bin/env python3
"""
Test the assistant by sending it messages
"""

import asyncio
import json
from datetime import datetime
from ctypes import CDLL, c_void_p, c_char_p, c_double
from pathlib import Path

def find_tdlib():
    paths = ['./tdlib/lib/libtdjson.dylib', './tdlib/build/libtdjson.dylib']
    for p in paths:
        if Path(p).exists():
            return p
    return None

async def send_test_message():
    """Send a test message to trigger response"""
    
    tdlib_path = find_tdlib()
    if not tdlib_path:
        print("TDLib not found")
        return
    
    tdlib = CDLL(tdlib_path)
    tdlib.td_json_client_create.restype = c_void_p
    tdlib.td_json_client_send.argtypes = [c_void_p, c_char_p]
    tdlib.td_json_client_receive.restype = c_char_p
    tdlib.td_json_client_receive.argtypes = [c_void_p, c_double]
    
    client = tdlib.td_json_client_create()
    
    def send(data):
        tdlib.td_json_client_send(client, json.dumps(data).encode('utf-8'))
    
    def receive(timeout=1.0):
        result = tdlib.td_json_client_receive(client, c_double(timeout))
        return json.loads(result.decode('utf-8')) if result else None
    
    # Send a message to yourself
    send({
        '@type': 'sendMessage',
        'chat_id': 7112538016,  # Your chat ID from the logs
        'input_message_content': {
            '@type': 'inputMessageText',
            'text': {
                '@type': 'formattedText',
                'text': f'🤖 Voice Assistant Test at {datetime.now().strftime("%H:%M:%S")}'
            }
        }
    })
    
    print("Test message sent!")
    
    # Wait for response
    for _ in range(10):
        update = receive(1.0)
        if update:
            print(f"Response: {update.get('@type')}")
        await asyncio.sleep(0.1)

asyncio.run(send_test_message())
