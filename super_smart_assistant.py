#!/usr/bin/env python3
"""
Super Smart AI Assistant with Advanced Capabilities
For intern-mayaagent | 2025-11-05 15:54:45 UTC
"""

import time
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import json
import random
import re
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import wikipedia
import wolframalpha
import threading
import queue
from collections import deque

load_dotenv()

class SuperSmartAssistant:
    def __init__(self):
        print("\n" + "="*70)
        print("🧠 SUPER SMART AI ASSISTANT v3.0")
        print("="*70)
        print(f"User: intern-mayaagent")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("="*70)
        
        # Core components
        pygame.mixer.init()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        # Advanced features
        self.memory = self.load_memory()
        self.context_history = deque(maxlen=10)  # Remember last 10 exchanges
        self.user_profile = self.load_user_profile()
        self.learning_data = []
        
        # Knowledge bases
        self.knowledge_base = self.load_knowledge_base()
        
        # API clients (optional)
        self.setup_apis()
        
        # Calibrate microphone
        print("\n🎤 Calibrating advanced audio processing...")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
        
        print("✅ Super intelligence activated!")
        print("="*70)
    
    def setup_apis(self):
        """Setup optional API connections for enhanced intelligence"""
        # OpenAI
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key != "sk-your-key-here":
                self.openai = OpenAI(api_key=api_key)
                self.has_openai = True
                print("✅ OpenAI GPT connected")
            else:
                self.has_openai = False
        except:
            self.has_openai = False
        
        # Wolfram Alpha (for complex calculations)
        try:
            app_id = os.getenv('WOLFRAM_APP_ID')
            if app_id:
                self.wolfram = wolframalpha.Client(app_id)
                self.has_wolfram = True
                print("✅ Wolfram Alpha connected")
            else:
                self.has_wolfram = False
        except:
            self.has_wolfram = False
        
        # Wikipedia
        try:
            wikipedia.set_lang("en")
            self.has_wikipedia = True
            print("✅ Wikipedia connected")
        except:
            self.has_wikipedia = False
    
    def load_memory(self):
        """Load persistent memory from file"""
        try:
            with open('assistant_memory.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "user_name": None,
                "preferences": {},
                "facts_learned": [],
                "conversations_count": 0,
                "favorite_topics": [],
                "personal_info": {}
            }
    
    def save_memory(self):
        """Save memory to file"""
        with open('assistant_memory.json', 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def load_user_profile(self):
        """Load or create user profile"""
        try:
            with open('user_profile.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "interaction_count": 0,
                "last_interaction": None,
                "interests": [],
                "language_style": "formal",
                "mood_history": []
            }
    
    def save_user_profile(self):
        """Save user profile"""
        with open('user_profile.json', 'w') as f:
            json.dump(self.user_profile, f, indent=2, default=str)
    
    def load_knowledge_base(self):
        """Load enhanced knowledge base"""
        return {
            "greetings": {
                "morning": ["Good morning! Hope you're having a great start to your day!",
                           "Morning! Ready to tackle the day together?"],
                "afternoon": ["Good afternoon! How's your day going?",
                             "Afternoon! What can I help you with?"],
                "evening": ["Good evening! How was your day?",
                           "Evening! Time to relax and chat!"],
                "night": ["Good night! Sleep well!",
                         "Night! Sweet dreams!"]
            },
            "emotions": {
                "happy": ["That's wonderful to hear!", "Your happiness makes me happy too!"],
                "sad": ["I'm sorry you're feeling down. Want to talk about it?",
                       "That sounds tough. I'm here to listen."],
                "angry": ["I understand you're frustrated. Take a deep breath.",
                         "That sounds really annoying. How can I help?"],
                "excited": ["Your excitement is contagious!", "That's amazing! Tell me more!"]
            },
            "topics": {
                "technology": ["AI is evolving rapidly", "The future of tech is fascinating"],
                "science": ["Science helps us understand our universe", "Every discovery opens new questions"],
                "philosophy": ["Life's big questions are worth pondering", "What we think shapes who we are"],
                "humor": ["Laughter is the best medicine", "A good joke can brighten any day"]
            }
        }
    
    def listen(self):
        """Enhanced listening with context awareness"""
        try:
            with self.mic as source:
                print("\n👂 Listening intelligently...")
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=7)
            
            print("🧠 Processing with advanced recognition...")
            
            # Try multiple recognition methods
            text = None
            try:
                text = self.recognizer.recognize_google(audio)
            except:
                try:
                    # Fallback to different language
                    text = self.recognizer.recognize_google(audio, language="en-IN")
                except:
                    pass
            
            if text:
                print(f"📝 Understood: '{text}'")
                # Add to context
                self.context_history.append({"type": "user", "text": text, "time": datetime.now()})
                # Analyze emotion
                emotion = self.detect_emotion(text)
                if emotion:
                    print(f"😊 Detected emotion: {emotion}")
                return text
            
            return None
            
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def detect_emotion(self, text):
        """Detect emotion in text"""
        text_lower = text.lower()
        
        happy_words = ["happy", "great", "awesome", "wonderful", "excited", "love", "amazing"]
        sad_words = ["sad", "depressed", "down", "unhappy", "crying", "terrible"]
        angry_words = ["angry", "mad", "frustrated", "annoyed", "hate", "furious"]
        
        for word in happy_words:
            if word in text_lower:
                return "happy"
        for word in sad_words:
            if word in text_lower:
                return "sad"
        for word in angry_words:
            if word in text_lower:
                return "angry"
        
        return None
    
    def speak(self, text, emotion=None):
        """Speak with emotion awareness"""
        print(f"🤖 AI: '{text}'")
        
        # Add to context
        self.context_history.append({"type": "ai", "text": text, "time": datetime.now()})
        
        # Adjust speech based on emotion
        slow = emotion == "sad"
        
        tts = gTTS(text=text, lang='en', slow=slow)
        temp_file = f"temp_audio_{int(time.time())}.mp3"
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def get_super_smart_response(self, user_input):
        """Generate highly intelligent responses"""
        
        if not user_input:
            return None
        
        user_lower = user_input.lower()
        
        # Update interaction count
        self.user_profile["interaction_count"] += 1
        self.user_profile["last_interaction"] = datetime.now()
        
        # 1. CHECK PERSONAL MEMORY
        if "my name is" in user_lower:
            name = user_input.split("my name is")[-1].strip().split()[0]
            self.memory["user_name"] = name
            self.save_memory()
            return f"Wonderful to meet you, {name}! I'll remember that. What interests you most?"
        
        if self.memory["user_name"] and "my name" in user_lower:
            return f"Of course I remember, {self.memory['user_name']}! We've talked {self.user_profile['interaction_count']} times now."
        
        # 2. TIME-AWARE RESPONSES
        current_hour = datetime.now().hour
        if "hello" in user_lower or "hi" in user_lower:
            if self.memory["user_name"]:
                name = self.memory["user_name"]
                if current_hour < 12:
                    return f"Good morning, {name}! Ready for a productive day?"
                elif current_hour < 17:
                    return f"Good afternoon, {name}! How's your day progressing?"
                else:
                    return f"Good evening, {name}! How was your day?"
            else:
                return "Hello! I'm your super smart assistant. What's your name?"
        
        # 3. WIKIPEDIA SEARCH
        if "who is" in user_lower or "what is" in user_lower or "tell me about" in user_lower:
            query = user_input.replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
            if self.has_wikipedia:
                try:
                    summary = wikipedia.summary(query, sentences=2)
                    return f"According to Wikipedia: {summary}"
                except:
                    pass
        
        # 4. ADVANCED MATH (Wolfram Alpha or local)
        if any(op in user_input for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided"]):
            if self.has_wolfram:
                try:
                    res = self.wolfram.query(user_input)
                    answer = next(res.results).text
                    return f"The answer is {answer}"
                except:
                    pass
            # Fallback to local calculation
            return self.calculate_advanced(user_input)
        
        # 5. WEATHER (using free API)
        if "weather" in user_lower:
            return self.get_weather_response()
        
        # 6. NEWS (mock or real API)
        if "news" in user_lower:
            return self.get_news_response()
        
        # 7. REMEMBER CONVERSATIONS
        if "remember" in user_lower:
            fact = user_input.replace("remember", "").replace("that", "").strip()
            self.memory["facts_learned"].append(fact)
            self.save_memory()
            return f"I'll remember that: {fact}. I now know {len(self.memory['facts_learned'])} things you've told me!"
        
        if "what do you remember" in user_lower or "what do you know about me" in user_lower:
            if self.memory["facts_learned"]:
                facts = "\n".join(f"• {fact}" for fact in self.memory["facts_learned"][-3:])
                return f"I remember:\n{facts}\nAnd {len(self.memory['facts_learned'])-3} more things!"
            return "Tell me about yourself! I'd love to learn."
        
        # 8. JOKES WITH CATEGORIES
        if "joke" in user_lower:
            if "programming" in user_lower or "coding" in user_lower:
                jokes = [
                    "Why do programmers prefer dark mode? Because light attracts bugs!",
                    "Why do Python programmers prefer snake_case? Because they can't C sharp!",
                    "A SQL query walks into a bar, sees two tables and asks: Can I join you?"
                ]
            else:
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "What do you call a bear with no teeth? A gummy bear!",
                    "Why did the scarecrow win an award? He was outstanding in his field!"
                ]
            return random.choice(jokes)
        
        # 9. LEARNING FROM USER
        if "i like" in user_lower or "i love" in user_lower:
            interest = user_input.split("like")[-1].split("love")[-1].strip()
            if interest not in self.user_profile["interests"]:
                self.user_profile["interests"].append(interest)
                self.save_user_profile()
            return f"Great! I'll remember you like {interest}. Want to know a fun fact about it?"
        
        # 10. CONTEXTUAL RESPONSES
        if len(self.context_history) > 2:
            # Check previous context
            last_ai = None
            for item in reversed(self.context_history):
                if item["type"] == "ai":
                    last_ai = item["text"]
                    break
            
            if last_ai and "fun fact" in last_ai.lower():
                # Provide a fun fact based on interests
                if self.user_profile["interests"]:
                    interest = random.choice(self.user_profile["interests"])
                    return f"Here's a fun fact about {interest}: Did you know that's one of the most searched topics online?"
        
        # 11. EMOTIONAL SUPPORT
        emotion = self.detect_emotion(user_input)
        if emotion:
            responses = self.knowledge_base["emotions"].get(emotion, ["I understand."])
            return random.choice(responses)
        
        # 12. GPT-4 FALLBACK (if available)
        if self.has_openai:
            try:
                # Include context
                messages = [
                    {"role": "system", "content": f"You are a super intelligent assistant. The user's name is {self.memory.get('user_name', 'friend')}. Be helpful, smart, and engaging."}
                ]
                
                # Add context from history
                for item in list(self.context_history)[-4:]:
                    role = "user" if item["type"] == "user" else "assistant"
                    messages.append({"role": role, "content": item["text"]})
                
                messages.append({"role": "user", "content": user_input})
                
                response = self.openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.8
                )
                return response.choices[0].message.content
            except:
                pass
        
        # 13. SMART FALLBACK
        # Analyze input for keywords and provide relevant response
        keywords_responses = {
            "help": f"I can help with math, facts, jokes, weather, remember things about you, and have intelligent conversations! You've asked me {self.user_profile['interaction_count']} questions so far.",
            "capabilities": "I can: remember conversations, learn about you, tell jokes, do complex math, search Wikipedia, provide emotional support, and much more!",
            "smart": "I use multiple AI systems, remember our conversations, learn from what you tell me, and adapt to your preferences!",
            "how are you": f"I'm functioning optimally! I've learned {len(self.memory['facts_learned'])} facts and had {self.user_profile['interaction_count']} interactions with you.",
            "favorite": f"Your interests include: {', '.join(self.user_profile['interests'][:3]) if self.user_profile['interests'] else 'Tell me what you like!'}"
        }
        
        for keyword, response in keywords_responses.items():
            if keyword in user_lower:
                return response
        
        # Final intelligent fallback
        return f"That's an interesting point about '{user_input}'. Based on our {self.user_profile['interaction_count']} conversations, I think you'd be interested to know more. What aspect intrigues you most?"
    
    def calculate_advanced(self, expression):
        """Advanced calculator with word problems"""
        try:
            # Convert words to numbers
            word_to_num = {
                "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
                "ten": 10, "eleven": 11, "twelve": 12, "twenty": 20,
                "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100
            }
            
            expr = expression.lower()
            for word, num in word_to_num.items():
                expr = expr.replace(word, str(num))
            
            # Handle operations
            expr = expr.replace("plus", "+").replace("add", "+")
            expr = expr.replace("minus", "-").replace("subtract", "-")
            expr = expr.replace("times", "*").replace("multiplied by", "*")
            expr = expr.replace("divided by", "/").replace("over", "/")
            
            # Extract and calculate
            import re
            numbers = re.findall(r'[\d.]+', expr)
            operators = re.findall(r'[+\-*/]', expr)
            
            if len(numbers) >= 2 and operators:
                result = eval(f"{numbers[0]}{operators[0]}{numbers[1]}")
                return f"The answer is {result}"
            
            return "I can solve math problems! Try: 'What's 15 plus 27?'"
        except:
            return "I can help with calculations. Try asking: 'What's 10 times 5?'"
    
    def get_weather_response(self):
        """Get weather response (mock or real)"""
        # You could integrate with a free weather API here
        responses = [
            "I don't have live weather access, but I recommend checking weather.com for accurate forecasts!",
            "Weather patterns are fascinating! While I can't check current conditions, I can tell you about meteorology!",
            f"The weather varies by location. You've asked me {self.user_profile['interaction_count']} questions - this is number {self.user_profile['interaction_count']}!"
        ]
        return random.choice(responses)
    
    def get_news_response(self):
        """Get news response"""
        topics = ["technology", "science", "world events", "innovations", "discoveries"]
        return f"While I don't have live news feeds, {random.choice(topics)} news is always fascinating! What specific topic interests you?"
    
    def run(self):
        """Main conversation loop with super intelligence"""
        print("\n🚀 SUPER INTELLIGENT FEATURES")
        print("="*70)
        print("""
ADVANCED CAPABILITIES:
• Remember your name and preferences
• Learn from conversations  
• Search Wikipedia
• Solve complex math
• Emotional intelligence
• Context awareness
• Conversation memory
• Personalized responses

SAY THINGS LIKE:
• "My name is [name]"
• "Remember that I like pizza"
• "What do you know about me?"
• "Who is Albert Einstein?"
• "Calculate 47 times 83"
• "Tell me a programming joke"
• "I'm feeling sad"
        """)
        print("="*70)
        
        input("\n▶️ Press ENTER when ready...")
        
        # Personalized greeting based on history
        if self.memory["user_name"]:
            greeting = f"Welcome back, {self.memory['user_name']}! "
            if self.user_profile["last_interaction"]:
                last_time = datetime.now() - self.user_profile["last_interaction"]
                if last_time.days > 0:
                    greeting += f"It's been {last_time.days} days since we last talked. "
            greeting += "What's on your brilliant mind today?"
        else:
            greeting = "Hello! I'm your super intelligent assistant. I can remember our conversations, learn about you, and provide smart responses. What's your name?"
        
        self.speak(greeting)
        
        silence_count = 0
        
        while True:
            try:
                user_input = self.listen()
                
                if not user_input:
                    silence_count += 1
                    if silence_count > 6:
                        prompts = [
                            f"Still here, {self.memory.get('user_name', 'friend')}! What would you like to explore?",
                            "Feel free to ask me anything - I'm learning and improving!",
                            f"Did you know we've had {self.user_profile['interaction_count']} interactions? Let's make this one count!"
                        ]
                        self.speak(random.choice(prompts))
                        silence_count = 0
                    continue
                
                silence_count = 0
                
                # Exit commands
                if any(bye in user_input.lower() for bye in ["goodbye", "bye", "exit", "quit", "see you"]):
                    # Save everything
                    self.save_memory()
                    self.save_user_profile()
                    
                    farewell = f"Goodbye{' ' + self.memory['user_name'] if self.memory['user_name'] else ''}! "
                    farewell += f"I've learned {len(self.memory['facts_learned'])} things from you. "
                    farewell += "Can't wait for our next conversation!"
                    self.speak(farewell)
                    break
                
                # Get super intelligent response
                response = self.get_super_smart_response(user_input)
                if response:
                    # Detect emotion for appropriate delivery
                    emotion = self.detect_emotion(user_input)
                    self.speak(response, emotion)
                
            except KeyboardInterrupt:
                break
        
        print(f"\n📊 Session Stats:")
        print(f"• Total interactions: {self.user_profile['interaction_count']}")
        print(f"• Facts learned: {len(self.memory['facts_learned'])}")
        print(f"• Topics discussed: {len(set(self.user_profile['interests']))}")
        print("\n✅ Super intelligent session ended!")

if __name__ == "__main__":
    assistant = SuperSmartAssistant()
    assistant.run()
