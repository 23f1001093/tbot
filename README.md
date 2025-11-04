📞 How Telegram AI Voice Assistant Works
Quick Overview
This project automatically answers Telegram voice calls and speaks with callers using AI - like having your own personal assistant that handles calls for you.

The Flow (What Happens)
Code
1. 📱 Someone calls your Telegram number
     ↓
2. 🤖 Bot detects the call (using TDLib)
     ↓
3. ✅ Bot auto-answers after 2 seconds
     ↓
4. 🎤 Caller speaks: "What's the weather?"
     ↓
5. 🔊 Bot listens and converts speech → text
     ↓
6. 🧠 AI (GPT-4) processes and generates response
     ↓
7. 🗣️ Bot converts response → speech
     ↓
8. 📞 Caller hears: "I don't have real-time weather data..."
     ↓
9. 🔄 Conversation continues naturally
Technical Components
1. Call Detection & Control
Uses TDLib (Telegram's official library) to monitor incoming calls
Automatically accepts calls programmatically
2. Speech Recognition
Captures caller's voice
Converts to text using Google Speech API
3. AI Processing
Sends text to GPT-4/Claude
Gets intelligent response based on context
4. Speech Synthesis
Converts AI text response to natural voice
Uses Google TTS or ElevenLabs
5. Audio Transmission
Challenge: Can't directly inject audio into mobile calls
Solution: Uses physical audio bridge (phone speaker → computer mic → AI → computer speaker → phone mic)
Current Limitations & Workarounds
The Problem: Telegram doesn't allow third-party apps to directly send audio in 1:1 calls (security feature).

Working Solutions:

Desktop: Virtual audio cable (BlackHole/VB-Cable)
Mobile: Physical audio bridge (phone on speaker near computer)
Alternative: Group voice chats (full programmatic control)
Requirements
Python 3.11+
Telegram API credentials
OpenAI API key
TDLib compiled library
Good internet connection
