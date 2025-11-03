"""
Audio utility functions
"""

import numpy as np
import wave
import io
from typing import Tuple, Optional

def convert_sample_rate(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Convert audio sample rate"""
    if orig_sr == target_sr:
        return audio
    
    from scipy import signal
    return signal.resample(audio, int(len(audio) * target_sr / orig_sr))

def audio_to_wav(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert audio array to WAV bytes"""
    buffer = io.BytesIO()
    
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        if audio.dtype != np.int16:
            audio = (audio * 32767).astype(np.int16)
        
        wav.writeframes(audio.tobytes())
    
    buffer.seek(0)
    return buffer.read()

def calculate_rms(audio: np.ndarray) -> float:
    """Calculate RMS of audio"""
    return np.sqrt(np.mean(audio.astype(np.float32) ** 2))

def normalize_audio(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    """Normalize audio to target dB"""
    rms = calculate_rms(audio)
    if rms > 0:
        target_rms = 10 ** (target_db / 20) * 32768
        gain = target_rms / rms
        return np.clip(audio * gain, -32768, 32767).astype(np.int16)
    return audio

class AudioUtils:
    """Audio utility class"""
    
    @staticmethod
    def is_silence(audio: np.ndarray, threshold: float = 0.01) -> bool:
        """Check if audio is silence"""
        rms = calculate_rms(audio) / 32768
        return rms < threshold
    
    @staticmethod
    def split_audio(audio: np.ndarray, chunk_size: int) -> list:
        """Split audio into chunks"""
        chunks = []
        for i in range(0, len(audio), chunk_size):
            chunks.append(audio[i:i + chunk_size])
        return chunks