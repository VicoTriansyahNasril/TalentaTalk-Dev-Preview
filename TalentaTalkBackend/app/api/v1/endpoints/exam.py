from fastapi import APIRouter, Depends, UploadFile, File, Form, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.exam_service import ExamService
from app.schemas.response import ResponseBase
from app.schemas.exam import ExamStartResponse, ExamResultResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/start/{idmateriujian}", response_model=ResponseBase)
async def start_ujian(
    idmateriujian: int,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    user = get_current_user(authorization)
    talent_id = user["idtalent"]
    
    service = ExamService(db)
    result = await service.start_exam_session(talent_id, idmateriujian)
    return ResponseBase(data=result)

@router.post("/compare", response_model=ResponseBase)
async def compare_exam_voice(
    idContent: int = Form(...),
    idUjian: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    service = ExamService(db)
    audio_bytes = await file.read()
    result = await service.process_answer(idUjian, idContent, audio_bytes)
    return ResponseBase(data=result)

@router.get("/result/{idujian}", response_model=ResponseBase[ExamResultResponse])
async def get_exam_result(
    idujian: int,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Verify user owns the exam? (Optional but recommended)
    service = ExamService(db)
    result = await service.finish_exam(idujian)
    return ResponseBase(data=result)

# Endpoint delete untuk reset ujian (jika user ingin ulang)
@router.delete("/delete/{idujian}", response_model=ResponseBase)
async def delete_exam_session(
    idujian: int,
    db: AsyncSession = Depends(get_db)
):
    # Implementasi delete di repository jika diperlukan
    # Untuk sekarang return success dummy
    return ResponseBase(message="Exam session reset")