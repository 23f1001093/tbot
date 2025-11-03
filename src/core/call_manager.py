"""
Call Manager - Handles voice call logic
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque
import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class CallManager:
    """
    Manages voice calls with AI processing
    """
    
    def __init__(self, tdlib_client, ai_components: Dict):
        """Initialize call manager"""
        self.tdlib = tdlib_client
        self.stt = ai_components['stt']
        self.tts = ai_components['tts']
        self.llm = ai_components['llm']
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        # Active calls
        self.active_calls: Dict[int, CallSession] = {}
        
        # Configuration from environment
        self.config = {
            'auto_answer': os.getenv('AUTO_ANSWER_CALLS', 'true').lower() == 'true',
            'record_calls': os.getenv('RECORD_CALLS', 'true').lower() == 'true',
            'max_duration': int(os.getenv('MAX_CALL_DURATION', '300')),
            'answer_delay': 2
        }
        
        # Register handlers
        self.tdlib.register_handler('on_incoming_call', self.on_incoming_call)
        self.tdlib.register_handler('on_call_ready', self.on_call_ready)
        self.tdlib.register_handler('on_call_ended', self.on_call_ended)
        
        logger.info("✅ Call Manager initialized")
    
    def _load_prompts(self) -> Dict:
        """Load prompts from YAML"""
        try:
            with open('config/prompts.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            return {
                'default': {
                    'greeting': "Hello! How can I help you?",
                    'goodbye': "Thank you for calling. Goodbye!",
                    'error': "Sorry, I didn't understand that."
                }
            }
    
    async def on_incoming_call(self, call: Dict[str, Any]):
        """Handle incoming call"""
        call_id = call['id']
        user_id = call.get('user_id')
        
        logger.info(f"📲 Incoming call {call_id} from user {user_id}")
        
        session = CallSession(call_id, user_id)
        self.active_calls[call_id] = session
        
        if self.config['auto_answer']:
            await asyncio.sleep(self.config['answer_delay'])
            await self.tdlib.accept_call(call_id)
            logger.info(f"✅ Auto-answered call {call_id}")
    
    async def on_call_ready(self, call: Dict[str, Any]):
        """Handle call when connected"""
        call_id = call['id']
        
        if call_id not in self.active_calls:
            self.active_calls[call_id] = CallSession(call_id, call.get('user_id'))
        
        session = self.active_calls[call_id]
        session.state = 'active'
        session.connected_time = datetime.utcnow()
        
        logger.info(f"🎙️ Call {call_id} is active")
        
        # Start processing
        session.tasks.append(
            asyncio.create_task(self.process_call(call_id))
        )
        
        # Send greeting
        greeting = self.prompts.get('default', {}).get('greeting', "Hello!")
        await self.send_voice_response(call_id, greeting)
    
    async def process_call(self, call_id: int):
        """Main call processing loop"""
        session = self.active_calls.get(call_id)
        if not session:
            return
        
        try:
            while session.state == 'active':
                # Check max duration
                if session.connected_time:
                    duration = (datetime.utcnow() - session.connected_time).total_seconds()
                    if duration > self.config['max_duration']:
                        logger.info(f"Call {call_id} exceeded max duration")
                        await self.tdlib.end_call(call_id, int(duration))
                        break
                
                # Process audio (placeholder for actual implementation)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error processing call {call_id}: {e}")
    
    async def send_voice_response(self, call_id: int, text: str):
        """Send voice response to call"""
        try:
            logger.info(f"🔊 Sending: {text[:50]}...")
            
            # Convert to speech
            audio_data = await self.tts.synthesize(text)
            
            # Send audio (placeholder - actual implementation needs WebRTC)
            logger.info(f"📤 Audio sent to call {call_id}")
            
        except Exception as e:
            logger.error(f"Error sending voice: {e}")
    
    async def on_call_ended(self, call: Dict[str, Any]):
        """Handle call end"""
        call_id = call['id']
        
        if call_id in self.active_calls:
            session = self.active_calls[call_id]
            session.state = 'ended'
            session.end_time = datetime.utcnow()
            
            # Cancel tasks
            for task in session.tasks:
                if not task.done():
                    task.cancel()
            
            # Calculate duration
            if session.connected_time and session.end_time:
                duration = (session.end_time - session.connected_time).total_seconds()
                logger.info(f"📵 Call {call_id} ended. Duration: {duration:.1f}s")
            
            # Cleanup
            del self.active_calls[call_id]


class CallSession:
    """Represents an active call session"""
    
    def __init__(self, call_id: int, user_id: Optional[int] = None):
        self.call_id = call_id
        self.user_id = user_id
        self.state = 'pending'
        self.start_time = datetime.utcnow()
        self.connected_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.conversation_history: List[Dict] = []
        self.audio_buffer = deque(maxlen=200)
        self.tasks: List[asyncio.Task] = []