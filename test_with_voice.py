#!/usr/bin/env python3
"""Test voice assistant with TTS"""

import os
import asyncio
from gtts import gTTS
import pygame
from io import BytesIO

# Initialize pygame for audio playback
pygame.mixer.init()

async def speak(text):
    """Convert text to speech and play it"""
    print(f"🔊 Speaking: {text}")
    
    # Generate speech
    tts = gTTS(text=text, lang='en', slow=False)
    
    # Save to memory
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    
    # Play audio
    pygame.mixer.music.load(audio_buffer)
    pygame.mixer.music.play()
    
    # Wait for audio to finish
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

async def test():
    """Test TTS"""
    await speak("Hello! I am your AI voice assistant.")
    await speak("I can answer your calls and have conversations.")
    await speak("Call me on Telegram to test!")

if __name__ == '__main__':
    asyncio.run(test())
