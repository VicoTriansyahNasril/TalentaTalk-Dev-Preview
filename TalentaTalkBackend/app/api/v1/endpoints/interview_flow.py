from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.interview_service import InterviewService
from app.schemas.response import ResponseBase
from app.schemas.conversation import ChatInput
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.get("/start", response_model=ResponseBase)
async def start_interview(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = InterviewService(db)
    session_id = str(uuid.uuid4()) 
    result = await service.start_session(session_id)

    return ResponseBase(data=result)

@router.get("/status", response_model=ResponseBase)
async def get_interview_status(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Resume session if exists"""
    service = InterviewService(db)
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return ResponseBase(success=False, message="Missing Session ID")
        
    result = await service.get_session_status(session_id)
    return ResponseBase(data=result.get("status"), success=result["success"])

@router.post("/answer", response_model=ResponseBase)
async def answer_question(
    request: Request,
    input_data: ChatInput,
    db: AsyncSession = Depends(get_db)
):
    service = InterviewService(db)
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return ResponseBase(success=False, message="Missing X-Session-ID header")
        
    result = await service.process_answer(session_id, input_data.user_input, input_data.duration)
    return ResponseBase(data=result)

@router.post("/summary", response_model=ResponseBase)
async def get_summary(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = InterviewService(db)
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
         return ResponseBase(success=False, message="Missing X-Session-ID header")

    result = await service.generate_summary(session_id, current_user["idtalent"])
    return ResponseBase(data=result)