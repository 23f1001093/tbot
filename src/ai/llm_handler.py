"""
LLM Handler with environment variable support
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional
import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handle AI response generation"""
    
    def __init__(self):
        """Initialize LLM with environment configuration"""
        self.provider = os.getenv('OPENAI_API_KEY') and 'openai' or 'fallback'
        
        if self.provider == 'openai':
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '150'))
            logger.info(f"✅ Using OpenAI: {self.model}")
        else:
            logger.warning("⚠️ No API keys found, using fallback responses")
            self.provider = 'fallback'
        
        # Load response templates
        self._load_responses()
    
    def _load_responses(self):
        """Load response templates"""
        try:
            with open('config/responses.yaml', 'r') as f:
                self.responses = yaml.safe_load(f)
        except:
            self.responses = {}
    
    async def generate_response(self, user_input: str, context: Dict) -> str:
        """Generate AI response"""
        try:
            if self.provider == 'openai':
                return await self._generate_openai(user_input, context)
            else:
                return self._generate_fallback(user_input)
                
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I apologize, I'm having trouble processing that."
    
    async def _generate_openai(self, user_input: str, context: Dict) -> str:
        """Generate using OpenAI"""
        try:
            import openai
            
            messages = [
                {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise."}
            ]
            
            # Add context
            for msg in context.get('conversation_history', [])[-5:]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            messages.append({"role": "user", "content": user_input})
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._generate_fallback(user_input)
    
    def _generate_fallback(self, user_input: str) -> str:
        """Generate fallback response"""
        user_input_lower = user_input.lower()
        
        # Check response templates
        for category in self.responses.values():
            for item in category:
                for pattern in item['pattern']:
                    if pattern in user_input_lower:
                        import random
                        return random.choice(item['responses'])
        
        # Default responses
        defaults = [
            "I understand. How can I help you with that?",
            "Tell me more about that.",
            "I see. What would you like to know?"
        ]
        
        import random
        return random.choice(defaults)