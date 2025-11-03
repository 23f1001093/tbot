"""
Tests for AI components
"""
import os
import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from src.ai.speech_to_text import SpeechToText
from src.ai.text_to_speech import TextToSpeech
from src.ai.llm_handler import LLMHandler

class TestSpeechToText:
    """Test speech to text functionality"""
    
    @pytest.fixture
    def stt(self):
        """Create STT instance"""
        with patch('src.ai.speech_to_text.sr.Recognizer'):
            return SpeechToText()
    
    @pytest.mark.asyncio
    async def test_transcribe_returns_text(self, stt):
        """Test successful transcription"""
        audio = np.random.randint(-32768, 32767, 16000, dtype=np.int16)
        
        with patch.object(stt.recognizer, 'recognize_google', return_value="Hello world"):
            result = await stt.transcribe(audio)
            
        assert result == "Hello world"
    
    @pytest.mark.asyncio
    async def test_transcribe_handles_silence(self, stt):
        """Test handling of silence/no speech"""
        audio = np.zeros(16000, dtype=np.int16)
        
        with patch.object(stt.recognizer, 'recognize_google', 
                         side_effect=Exception("Could not understand")):
            result = await stt.transcribe(audio)
            
        assert result is None

class TestTextToSpeech:
    """Test text to speech functionality"""
    
    @pytest.fixture
    def tts(self):
        """Create TTS instance"""
        return TextToSpeech()
    
    @pytest.mark.asyncio
    async def test_synthesize_returns_audio(self, tts):
        """Test successful synthesis"""
        text = "Hello world"
        
        with patch('src.ai.text_to_speech.gTTS'):
            result = await tts.synthesize(text)
            
        assert result is not None
        assert isinstance(result, (np.ndarray, type(None)))
    
    @pytest.mark.asyncio
    async def test_synthesize_handles_empty_text(self, tts):
        """Test handling of empty text"""
        result = await tts.synthesize("")
        
        # Should handle gracefully
        assert result is None or len(result) == 0

class TestLLMHandler:
    """Test LLM handler functionality"""
    
    @pytest.fixture
    def llm(self):
        """Create LLM handler instance"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            return LLMHandler()
    
    @pytest.mark.asyncio
    async def test_generate_response(self, llm):
        """Test response generation"""
        user_input = "Hello"
        context = {'conversation_history': []}
        
        # Test fallback (no API call)
        llm.provider = 'fallback'
        response = await llm.generate_response(user_input, context)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_generate_with_context(self, llm):
        """Test response with conversation context"""
        user_input = "What did I just say?"
        context = {
            'conversation_history': [
                {'role': 'user', 'content': 'My name is John'},
                {'role': 'assistant', 'content': 'Nice to meet you, John!'}
            ]
        }
        
        llm.provider = 'fallback'
        response = await llm.generate_response(user_input, context)
        
        assert isinstance(response, str)