"""
Tests for TDLib client
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, MagicMock
from src.core.tdlib_client import TDLibClient

class TestTDLibClient:
    """Test TDLib client functionality"""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("TELEGRAM_API_ID", "123456")
        monkeypatch.setenv("TELEGRAM_API_HASH", "test_hash")
        monkeypatch.setenv("TELEGRAM_PHONE_NUMBER", "+1234567890")
    
    @pytest.fixture
    def client(self, mock_env):
        """Create TDLib client instance"""
        with patch('src.core.tdlib_client.CDLL'):
            client = TDLibClient()
            client.tdjson = MagicMock()
            return client
    
    def test_init_loads_credentials(self, client):
        """Test that credentials are loaded from environment"""
        assert client.api_id == 123456
        assert client.api_hash == "test_hash"
        assert client.phone_number == "+1234567890"
    
    def test_validates_non_default_credentials(self, mock_env):
        """Test credential validation"""
        with patch('src.core.tdlib_client.CDLL'):
            client = TDLibClient()
            # Should not raise error with valid credentials
            assert client.api_id != 12345678
    
    @pytest.mark.asyncio
    async def test_start_initializes_client(self, client):
        """Test client initialization"""
        client.tdjson.td_json_client_create.return_value = Mock()
        
        with patch.object(client, '_authenticate', return_value=None):
            await client.start()
            
        assert client._running is True
        client.tdjson.td_json_client_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_accept_call(self, client):
        """Test accepting a call"""
        call_id = 123
        
        with patch.object(client, '_send') as mock_send:
            await client.accept_call(call_id)
            
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args['@type'] == 'acceptCall'
        assert call_args['call_id'] == call_id
    
    def test_register_handler(self, client):
        """Test handler registration"""
        handler = Mock()
        client.register_handler('test_event', handler)
        
        assert 'test_event' in client.call_handlers
        assert client.call_handlers['test_event'] == handler
    
    @pytest.mark.asyncio
    async def test_handle_incoming_call(self, client):
        """Test handling incoming call"""
        call = {
            'id': 123,
            'state': {'@type': 'callStatePending'},
            'is_outgoing': False
        }
        
        handler = Mock()
        client.register_handler('on_incoming_call', handler)
        
        await client._handle_call_update(call)
        
        assert 123 in client.active_calls
        handler.assert_called_once_with(call)