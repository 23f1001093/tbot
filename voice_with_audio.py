#!/usr/bin/env python3
"""
Voice Assistant with actual audio support using tgcalls
"""

import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

# Use Telethon + PyTgCalls for voice
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
phone = os.getenv('TELEGRAM_PHONE_NUMBER')

# Create client
client = TelegramClient('voice_session', api_id, api_hash)
app = PyTgCalls(client)

@app.on_stream_end()
async def on_stream_end(client: PyTgCalls, update: Update):
    print("Stream ended")

@app.on_call_state_changed()
async def on_call_state(client: PyTgCalls, update: Update):
    print(f"Call state: {update}")

async def main():
    await client.start(phone=phone)
    await app.start()
    
    print("Voice assistant ready!")
    print("Waiting for calls...")
    
    # Keep running
    await asyncio.Event().wait()

asyncio.run(main())
