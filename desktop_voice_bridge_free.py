#!/usr/bin/env python3
"""
Voice Bridge with Free AI Alternatives
For intern-mayaagent | 2025-11-05 15:43:26 UTC
"""

import time
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DesktopVoiceBridge:
    def __init__(self):
        print("\n" + "="*70)
        print("🎙️ VOICE BRIDGE - FREE AI VERSION")
        print("="*70)
        print(f"User: intern-mayaagent")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("="*70)
        
        pygame.mixer.init()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        print("\n🎤 Calibrating microphone...")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✅ Ready! Using smart responses (no API needed)")
        print("="*70)
        
        # Joke database
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a fake noodle? An impasta!",
            "Why did the coffee file a police report? It got mugged!",
            "Why don't skeletons fight each other? They don't have the guts!"
        ]
        
    def listen(self):
        try:
            with self.mic as source:
                print("\n👂 Listening...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"📝 Heard: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def speak(self, text):
        print(f"🤖 AI says: '{text}'")
        
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = f"temp_audio_{int(time.time())}.mp3"
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def get_smart_response(self, user_input):
        """Smart responses without API"""
        user_lower = user_input.lower()
        
        # Jokes
        if "joke" in user_lower:
            return random.choice(self.jokes)
        
        # Bhojpuri movie
        elif "bhojpuri" in user_lower and "movie" in user_lower:
            movies = [
                "Some popular Bhojpuri movies are: Sasura Bada Paisawala, Nirahua Hindustani, and Raja Babu.",
                "Bhojpuri cinema has grown significantly! Stars like Dinesh Lal Yadav and Khesari Lal are very popular.",
                "Did you know? Bhojpuri film industry is one of the fastest growing regional cinemas in India!"
            ]
            return random.choice(movies)
        
        # Math
        elif "2+2" in user_lower.replace(" ", "") or "2 + 2" in user_lower:
            return "2 plus 2 equals 4."
        elif "5+3" in user_lower.replace(" ", "") or "5 + 3" in user_lower:
            return "5 plus 3 equals 8."
        elif "10-5" in user_lower.replace(" ", "") or "10 - 5" in user_lower:
            return "10 minus 5 equals 5."
        
        # Time and date
        elif "time" in user_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        elif "date" in user_lower or "day" in user_lower:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}."
        
        # Weather
        elif "weather" in user_lower:
            return "I can't check live weather, but it's always a good day to smile!"
        
        # Greetings
        elif "hello" in user_lower or "hi" in user_lower:
            greetings = [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! Nice to hear from you. How can I assist?"
            ]
            return random.choice(greetings)
        
        elif "how are you" in user_lower:
            return "I'm doing great! Thanks for asking. How are you?"
        
        # Name
        elif "your name" in user_lower or "who are you" in user_lower:
            return "I'm your AI assistant running through Telegram Desktop. You can call me Assistant!"
        
        # Capabilities
        elif "what can you do" in user_lower or "help" in user_lower:
            return "I can tell jokes, answer questions, tell time and date, and have conversations with you!"
        
        # Songs
        elif "sing" in user_lower or "song" in user_lower:
            return "La la la... I'm not the best singer, but I try! Would you like to hear a joke instead?"
        
        # Food
        elif "hungry" in user_lower or "food" in user_lower:
            foods = [
                "How about some pizza? Everyone loves pizza!",
                "Indian food sounds great - maybe some biryani?",
                "A nice sandwich is always a good choice!"
            ]
            return random.choice(foods)
        
        # Thank you
        elif "thank" in user_lower:
            return "You're welcome! Happy to help!"
        
        # Good responses for unclear inputs
        elif len(user_input.split()) < 3:
            return "Could you tell me more about that?"
        else:
            responses = [
                "That's interesting! Tell me more.",
                "I see what you mean. What else would you like to know?",
                "Thanks for sharing that with me!",
                f"You mentioned {user_input}. That sounds interesting!"
            ]
            return random.choice(responses)
    
    def run(self):
        print("\n📋 SETUP INSTRUCTIONS")
        print("="*70)
        print("""
1. Open TELEGRAM DESKTOP
2. Make or receive a voice call  
3. Put call on SPEAKER
4. Press ENTER here to start
5. Say "goodbye" to end

TRY SAYING: "Tell me a joke" or "What time is it?"
        """)
        print("="*70)
        
        input("\n▶️ Press ENTER when call is active...")
        
        self.speak("Hello! I'm your AI assistant. I can tell jokes, answer questions, and chat with you!")
        
        silence_count = 0
        
        while True:
            try:
                user_input = self.listen()
                
                if not user_input:
                    silence_count += 1
                    if silence_count > 3:
                        self.speak("Are you still there?")
                        silence_count = 0
                    continue
                
                silence_count = 0
                
                if "goodbye" in user_input.lower() or "bye" in user_input.lower():
                    self.speak("Goodbye! Have a wonderful day!")
                    break
                
                response = self.get_smart_response(user_input)
                self.speak(response)
                
            except KeyboardInterrupt:
                break
        
        print("\n✅ Session ended successfully!")

if __name__ == "__main__":
    bridge = DesktopVoiceBridge()
    bridge.run()
