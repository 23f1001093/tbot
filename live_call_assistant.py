#!/usr/bin/env python3
"""
WORKING 1:1 Voice Call AI Assistant
Uses Virtual Audio Cable to transmit AI responses
"""

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from gtts import gTTS
import os
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LiveCallAssistant:
    def __init__(self):
        print("\n" + "="*70)
        print("🤖 LIVE 1:1 TELEGRAM VOICE CALL ASSISTANT")
        print("="*70)
        
        # OpenAI setup
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No OPENAI_API_KEY found in .env file")
            exit(1)
        
        self.openai = OpenAI(api_key=api_key)
        self.conversation = []
        
        # Find BlackHole device
        self.find_virtual_device()
        
    def find_virtual_device(self):
        """Find BlackHole virtual audio device"""
        devices = sd.query_devices()
        
        print("\n📡 Available Audio Devices:")
        for i, device in enumerate(devices):
            name = device['name']
            print(f"  [{i}] {name}")
            if 'BlackHole' in name or 'VB-Cable' in name:
                self.virtual_device = i
                print(f"      ✅ Using this as virtual microphone")
        
        if not hasattr(self, 'virtual_device'):
            print("\n❌ ERROR: No virtual audio device found!")
            print("Please install BlackHole:")
            print("  brew install blackhole-2ch")
            exit(1)
    
    def speak(self, text):
        """Speak through virtual device (Telegram will transmit this)"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] 🤖 AI: {text}")
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        audio_file = f"temp_speech_{int(time.time())}.mp3"
        tts.save(audio_file)
        
        try:
            # Load and play through virtual device
            data, samplerate = sf.read(audio_file)
            sd.play(data, samplerate, device=self.virtual_device)
            sd.wait()  # Wait until finished
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
        finally:
            # Cleanup
            if os.path.exists(audio_file):
                os.remove(audio_file)
    
    def listen(self, timeout=10):
        """Listen to user through default microphone"""
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 👂 Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            
            # Convert to text
            text = recognizer.recognize_google(audio)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 👤 User: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("⚠️ Couldn't understand audio")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_ai_response(self, user_text):
        """Get AI response from OpenAI"""
        self.conversation.append({
            "role": "user",
            "content": user_text
        })
        
        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise and natural for voice conversation."},
                *self.conversation
            ]
        )
        
        ai_text = response.choices[0].message.content
        
        self.conversation.append({
            "role": "assistant",
            "content": ai_text
        })
        
        return ai_text
    
    def run(self):
        """Main conversation loop"""
        print("\n" + "="*70)
        print("📋 SETUP INSTRUCTIONS")
        print("="*70)
        print("\n1️⃣  Open Telegram Desktop")
        print("2️⃣  Go to: Settings → Advanced → Voice and Video")
        print(f"3️⃣  Set Microphone to: BlackHole 2ch (device {self.virtual_device})")
        print("4️⃣  Accept an incoming call OR call someone")
        print("5️⃣  Once call is connected, come back here")
        print("\n" + "="*70)
        
        input("\n▶️  Press ENTER when the call is connected and ready...")
        
        print("\n✅ Starting conversation...")
        
        # Initial greeting
        self.speak("Hello! I'm your AI assistant. How can I help you today?")
        
        # Main loop
        turn_count = 0
        while True:
            try:
                turn_count += 1
                print(f"\n--- Turn {turn_count} ---")
                
                # Listen for user
                user_input = self.listen(timeout=15)
                
                if not user_input:
                    # No input detected
                    if turn_count == 1:
                        self.speak("I didn't catch that. Could you please repeat?")
                    continue
                
                # Check for exit commands
                if any(word in user_input.lower() for word in ['goodbye', 'bye', 'end call', 'hang up']):
                    self.speak("Goodbye! It was nice talking to you. Have a great day!")
                    break
                
                # Get AI response
                ai_response = self.get_ai_response(user_input)
                
                # Speak the response
                self.speak(ai_response)
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error in conversation loop: {e}")
                break
        
        print("\n" + "="*70)
        print("✅ Conversation ended")
        print(f"Total turns: {turn_count}")
        print("="*70 + "\n")

if __name__ == "__main__":
    assistant = LiveCallAssistant()
    assistant.run()
