"""
Text to Speech Module with environment variable support
"""

import os
import logging
import numpy as np
import io
from typing import Optional
from gtts import gTTS
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Text to speech conversion"""
    
    def __init__(self):
        """Initialize TTS with environment configuration"""
        self.provider = os.getenv('TTS_PROVIDER', 'gtts')
        self.language = os.getenv('TTS_LANGUAGE', 'en')
        self.voice = os.getenv('TTS_VOICE', 'default')
        
        # Check for API keys if using premium services
        if self.provider == 'elevenlabs':
            self.api_key = os.getenv('ELEVENLABS_API_KEY')
            if not self.api_key:
                logger.warning("ElevenLabs API key not found, falling back to gTTS")
                self.provider = 'gtts'
        
        logger.info(f"✅ TTS initialized: {self.provider}, language: {self.language}")
    
    async def synthesize(self, text: str) -> Optional[np.ndarray]:
        """Convert text to speech"""
        try:
            if self.provider == 'gtts':
                return await self._synthesize_gtts(text)
            elif self.provider == 'elevenlabs':
                return await self._synthesize_elevenlabs(text)
            else:
                return await self._synthesize_gtts(text)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    async def _synthesize_gtts(self, text: str) -> Optional[np.ndarray]:
        """Use Google TTS (free)"""
        try:
            tts = gTTS(text=text, lang=self.language, slow=False)
            
            mp3_buffer = io.BytesIO()
            tts.write_to_fp(mp3_buffer)
            mp3_buffer.seek(0)
            
            # Convert to audio array
            audio = AudioSegment.from_mp3(mp3_buffer)
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            samples = np.array(audio.get_array_of_samples())
            
            logger.info(f"🔊 Synthesized {len(text)} chars")
            return samples
            
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return None
    
    async def _synthesize_elevenlabs(self, text: str) -> Optional[np.ndarray]:
        """Use ElevenLabs API (premium)"""
        if not self.api_key:
            return await self._synthesize_gtts(text)
        
        try:
            import aiohttp
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice}"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        # Convert to numpy array
                        audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
                        audio = audio.set_frame_rate(16000).set_channels(1)
                        
                        return np.array(audio.get_array_of_samples())
                    else:
                        logger.error(f"ElevenLabs API error: {response.status}")
                        return await self._synthesize_gtts(text)
                        
        except Exception as e:
            logger.error(f"ElevenLabs error: {e}")
            return await self._synthesize_gtts(text)