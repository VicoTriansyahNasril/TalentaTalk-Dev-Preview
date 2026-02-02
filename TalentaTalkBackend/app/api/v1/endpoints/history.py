from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.history_repository import HistoryRepository
from app.schemas.response import ResponseBase
from app.utils.time_utils import TimeUtils

router = APIRouter()

@router.get("/phoneme", response_model=ResponseBase)
async def get_phoneme_history(
    page: int = 1, size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    talent_id = 1
    repo = HistoryRepository(db)
    items = await repo.get_phoneme_history(talent_id, skip=(page-1)*size, limit=size)
    
    data = []
    for item in items:
        raw = item["raw"]
        data.append({
            "idsoal": raw.idsoal,
            "typelatihan": raw.typelatihan,
            "soal": item["soal_text"],
            "nilai": raw.nilai,
            "waktulatihan": TimeUtils.format_to_wib(raw.waktulatihan),
            "phoneme_comparison": raw.phoneme_comparison
        })
    return ResponseBase(data=data)

@router.get("/conversation", response_model=ResponseBase)
async def get_conversation_history(
    db: AsyncSession = Depends(get_db)
):
    talent_id = 1
    repo = HistoryRepository(db)
    rows = await repo.get_conversation_history(talent_id)
    
    data = []
    for model, topic in rows:
        data.append({
            "topic": topic,
            "wpm": model.wpm,
            "grammar": model.grammar,
            "waktulatihan": TimeUtils.format_to_wib(model.waktulatihan)
        })
    return ResponseBase(data=data)

@router.get("/exam", response_model=ResponseBase)
async def get_exam_history(
    db: AsyncSession = Depends(get_db)
):
    talent_id = 1
    repo = HistoryRepository(db)
    history_data = await repo.get_exam_history(talent_id)
    
    formatted_data = []
    for h in history_data:
        exam = h["exam"]
        formatted_data.append({
            "idujian": exam.idujian,
            "kategori": exam.kategori,
            "nilai_total": exam.nilai,
            "waktuujian": TimeUtils.format_to_wib(exam.waktuujian),
            "details": h["details"]
        })
    return ResponseBase(data=formatted_data)