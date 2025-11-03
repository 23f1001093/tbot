"""
Conversation Context Manager
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manage conversation context and history"""
    
    def __init__(self, call_id: int):
        """Initialize conversation manager"""
        self.call_id = call_id
        self.history: List[Dict] = []
        self.context: Dict = {}
        self.start_time = datetime.utcnow()
        
        # Storage path
        self.storage_path = Path(f"./data/conversations/{call_id}")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def add_message(self, role: str, content: str):
        """Add message to conversation"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.history.append(message)
        
        # Update context
        if role == 'user':
            self._extract_context(content)
    
    def _extract_context(self, text: str):
        """Extract context from user message"""
        # Simple context extraction
        text_lower = text.lower()
        
        # Extract potential name
        if 'my name is' in text_lower:
            parts = text_lower.split('my name is')
            if len(parts) > 1:
                name = parts[1].strip().split()[0]
                self.context['user_name'] = name
        
        # Extract intent
        intents = {
            'greeting': ['hello', 'hi', 'hey'],
            'help': ['help', 'assist', 'support'],
            'information': ['what', 'when', 'where', 'how'],
            'farewell': ['bye', 'goodbye', 'see you']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                self.context['last_intent'] = intent
                break
    
    def get_context(self) -> Dict:
        """Get current context"""
        return {
            'conversation_history': self.history[-10:],  # Last 10 messages
            'context': self.context,
            'call_duration': (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    def save(self):
        """Save conversation to file"""
        try:
            filename = self.storage_path / f"{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            
            data = {
                'call_id': self.call_id,
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.utcnow().isoformat(),
                'history': self.history,
                'context': self.context
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Conversation saved: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    def get_summary(self) -> str:
        """Get conversation summary"""
        if not self.history:
            return "No conversation"
        
        num_messages = len(self.history)
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        return f"Messages: {num_messages}, Duration: {duration:.1f}s"