"""
Audio Processor - Handles audio format conversions and processing
"""

import logging
import numpy as np
import io
import wave
from typing import Optional, Tuple, Dict
from scipy import signal
import struct

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Process audio for voice calls
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize audio processor"""
        self.config = config or {}
        
        # Audio parameters
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.channels = self.config.get('channels', 1)
        self.frame_duration_ms = self.config.get('frame_duration_ms', 20)
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
        logger.info(f"✅ Audio processor initialized: {self.sample_rate}Hz, {self.channels}ch")
    
    def convert_to_pcm(self, audio_data: bytes, input_format: str = 'opus') -> np.ndarray:
        """Convert audio to PCM format"""
        try:
            if input_format == 'opus':
                # Placeholder for Opus decoding
                # In production, use opus library
                return np.frombuffer(audio_data, dtype=np.int16)
            elif input_format == 'wav':
                return self._decode_wav(audio_data)
            else:
                logger.warning(f"Unknown format: {input_format}")
                return np.array([], dtype=np.int16)
                
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return np.array([], dtype=np.int16)
    
    def _decode_wav(self, wav_data: bytes) -> np.ndarray:
        """Decode WAV data"""
        try:
            with io.BytesIO(wav_data) as wav_buffer:
                with wave.open(wav_buffer, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    return np.frombuffer(frames, dtype=np.int16)
        except Exception as e:
            logger.error(f"Error decoding WAV: {e}")
            return np.array([], dtype=np.int16)
    
    def encode_to_opus(self, pcm_data: np.ndarray) -> bytes:
        """Encode PCM to Opus format"""
        # Placeholder - in production use opus library
        return pcm_data.astype(np.int16).tobytes()
    
    def resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        if orig_sr == target_sr:
            return audio
        
        try:
            # Calculate resample ratio
            ratio = target_sr / orig_sr
            new_length = int(len(audio) * ratio)
            
            # Resample using scipy
            resampled = signal.resample(audio, new_length)
            
            return resampled.astype(audio.dtype)
            
        except Exception as e:
            logger.error(f"Error resampling: {e}")
            return audio
    
    def apply_noise_reduction(self, audio: np.ndarray) -> np.ndarray:
        """Apply noise reduction to audio"""
        try:
            # Simple noise gate
            threshold = np.max(np.abs(audio)) * 0.1
            audio[np.abs(audio) < threshold] *= 0.1
            return audio
        except Exception as e:
            logger.error(f"Error in noise reduction: {e}")
            return audio
    
    def normalize_audio(self, audio: np.ndarray, target_level: float = -3.0) -> np.ndarray:
        """Normalize audio level"""
        try:
            # Calculate current RMS
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
            
            if rms > 0:
                # Calculate target RMS (in linear scale)
                target_rms = 10 ** (target_level / 20) * 32768
                
                # Calculate gain
                gain = target_rms / rms
                
                # Apply gain with clipping protection
                normalized = audio * gain
                normalized = np.clip(normalized, -32768, 32767)
                
                return normalized.astype(np.int16)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio
    
    def detect_silence(self, audio: np.ndarray, threshold: float = 0.01) -> bool:
        """Detect if audio is silence"""
        try:
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2)) / 32768
            return rms < threshold
        except:
            return False
    
    def create_wav_header(self, audio_data: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
        """Create WAV header for raw PCM data"""
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            len(audio_data) + 36,
            b'WAVE',
            b'fmt ',
            16,  # PCM
            1,   # Format
            channels,
            sample_rate,
            sample_rate * channels * 2,
            channels * 2,
            16,  # Bits per sample
            b'data',
            len(audio_data)
        )
        return wav_header + audio_data