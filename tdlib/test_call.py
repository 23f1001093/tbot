"""
Tests for call handling
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from src.core.call_manager import CallManager, CallSession

class TestCallManager:
    """Test call management functionality"""
    
    @pytest.fixture
    def tdlib_client(self):
        """Mock TDLib client"""
        client = Mock()
        client.accept_call = AsyncMock()
        client.end_call = AsyncMock()
        client.register_handler = Mock()
        return client
    
    @pytest.fixture
    def ai_components(self):
        """Mock AI components"""
        return {
            'stt': Mock(transcribe=AsyncMock(return_value="Hello")),
            'tts': Mock(synthesize=AsyncMock(return_value=b"audio")),
            'llm': Mock(generate_response=AsyncMock(return_value="Hi there"))
        }
    
    @pytest.fixture
    def manager(self, tdlib_client, ai_components):
        """Create call manager instance"""
        return CallManager(tdlib_client, ai_components)
    
    @pytest.mark.asyncio
    async def test_incoming_call_auto_answer(self, manager, tdlib_client):
        """Test auto-answering incoming calls"""
        call = {
            'id': 123,
            'user_id': 456
        }
        
        manager.config['auto_answer'] = True
        await manager.on_incoming_call(call)
        
        # Wait for auto-answer delay
        await asyncio.sleep(2.1)
        
        tdlib_client.accept_call.assert_called_once_with(123)
        assert 123 in manager.active_calls
    
    @pytest.mark.asyncio
    async def test_call_ready_starts_processing(self, manager):
        """Test that call ready starts processing"""
        call = {
            'id': 123,
            'user_id': 456
        }
        
        await manager.on_call_ready(call)
        
        assert 123 in manager.active_calls
        session = manager.active_calls[123]
        assert session.state == 'active'
        assert len(session.tasks) > 0
    
    @pytest.mark.asyncio
    async def test_call_ended_cleanup(self, manager):
        """Test cleanup when call ends"""
        call_id = 123
        manager.active_calls[call_id] = CallSession(call_id, 456)
        
        call = {'id': call_id}
        await manager.on_call_ended(call)
        
        assert call_id not in manager.active_calls
    
    @pytest.mark.asyncio
    async def test_send_voice_response(self, manager, ai_components):
        """Test sending voice response"""
        call_id = 123
        text = "Hello there"
        
        await manager.send_voice_response(call_id, text)
        
        ai_components['tts'].synthesize.assert_called_once_with(text)

class TestCallSession:
    """Test call session functionality"""
    
    def test_session_initialization(self):
        """Test session is properly initialized"""
        session = CallSession(123, 456)
        
        assert session.call_id == 123
        assert session.user_id == 456
        assert session.state == 'pending'
        assert isinstance(session.start_time, datetime)
        assert len(session.conversation_history) == 0
    
    def test_session_state_tracking(self):
        """Test session state changes"""
        session = CallSession(123)
        
        assert session.state == 'pending'
        
        session.state = 'active'
        session.connected_time = datetime.utcnow()
        assert session.state == 'active'
        
        session.state = 'ended'
        session.end_time = datetime.utcnow()
        assert session.state == 'ended'