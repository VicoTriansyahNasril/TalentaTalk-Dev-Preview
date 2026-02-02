import io
import logging
import numpy as np
import librosa
import torch
import whisper
import os
import tempfile
from transformers import AutoProcessor, AutoModelForCTC
from starlette.concurrency import run_in_threadpool
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

class AudioService:
    # --- PHONEME MODELS (Wav2Vec2) ---
    _phoneme_processor = None
    _phoneme_model = None
    _sampling_rate = 16000
    
    # --- TEXT MODEL (Whisper) ---
    _whisper_model = None

    @classmethod
    def _load_phoneme_model(cls):
        if cls._phoneme_processor is None or cls._phoneme_model is None:
            try:
                print("Loading Wav2Vec2 Model...")
                cls._phoneme_processor = AutoProcessor.from_pretrained("bookbot/wav2vec2-ljspeech-gruut")
                cls._phoneme_model = AutoModelForCTC.from_pretrained("bookbot/wav2vec2-ljspeech-gruut")
            except Exception as e:
                logger.error(f"Failed to load Phoneme model: {e}")
                raise AppError(status_code=500, detail="Phoneme processing unavailable")

    @classmethod
    def _load_whisper_model(cls):
        if cls._whisper_model is None:
            try:
                print("Loading Whisper Model...")
                cls._whisper_model = whisper.load_model("small") # Bisa ganti 'base' atau 'tiny' agar lebih cepat
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise AppError(status_code=500, detail="Text transcription unavailable")

    @classmethod
    def _process_phoneme_sync(cls, audio_bytes: bytes) -> str:
        cls._load_phoneme_model()
        try:
            audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=cls._sampling_rate)
            audio = audio / np.max(np.abs(audio)) # Normalize

            inputs = cls._phoneme_processor(
                audio, 
                return_tensors="pt", 
                sampling_rate=cls._sampling_rate, 
                padding=True
            )
            
            with torch.no_grad():
                logits = cls._phoneme_model(inputs.input_values).logits
            
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = cls._phoneme_processor.batch_decode(predicted_ids)[0]
            
            return transcription.strip()
            
        except Exception as e:
            logger.error(f"Phoneme processing error: {e}")
            raise AppError(status_code=400, detail="Failed to process audio file")

    @classmethod
    def _process_whisper_sync(cls, audio_bytes: bytes) -> str:
        cls._load_whisper_model()
        try:
            # Whisper butuh file path, jadi kita buat temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            try:
                result = cls._whisper_model.transcribe(temp_path, language="en")
                return result["text"].strip()
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Whisper processing error: {e}")
            raise AppError(status_code=400, detail="Failed to transcribe text")

    @classmethod
    async def transcribe(cls, audio_bytes: bytes) -> str:
        """Transcribe to Phonemes (Async wrapper)"""
        return await run_in_threadpool(cls._process_phoneme_sync, audio_bytes)

    @classmethod
    async def transcribe_text(cls, audio_bytes: bytes) -> str:
        """Transcribe to English Text (Async wrapper for Whisper)"""
        return await run_in_threadpool(cls._process_whisper_sync, audio_bytes)