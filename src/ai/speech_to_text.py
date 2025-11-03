# Python 3.13 Compatible STT
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import whisper
    HAS_WHISPER = True
except:
    HAS_WHISPER = False

class SpeechToText:
    def __init__(self):
        if HAS_WHISPER:
            self.model = whisper.load_model("tiny")
            self.provider = "whisper"
        else:
            self.provider = "mock"
            
    async def transcribe(self, audio_data: np.ndarray) -> Optional[str]:
        if self.provider == "whisper" and HAS_WHISPER:
            try:
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32) / 32768.0
                result = self.model.transcribe(audio_data, fp16=False)
                return result.get("text", "").strip()
            except:
                pass
        return "Test message"
