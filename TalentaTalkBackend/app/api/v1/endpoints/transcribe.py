from fastapi import APIRouter, UploadFile, File
from app.services.audio_service import AudioService
from app.schemas.response import ResponseBase

router = APIRouter()

@router.post("/transcribe", response_model=ResponseBase)
async def transcribe_audio(file: UploadFile = File(...)):
    """General purpose speech-to-text using Whisper"""
    content = await file.read()
    text = await AudioService.transcribe_text(content)
    return ResponseBase(data={"text": text})