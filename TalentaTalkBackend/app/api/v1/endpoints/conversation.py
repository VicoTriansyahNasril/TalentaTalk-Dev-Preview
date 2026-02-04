from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import ChatInput, ChatResponse, ConversationStart, TopicListResponse
from app.schemas.response import ResponseBase
from app.api.deps import get_current_user
from app.models.models import Hasillatihanpercakapan

router = APIRouter()

@router.get("/topics", response_model=ResponseBase[TopicListResponse])
async def get_topics(db: AsyncSession = Depends(get_db)):
    service = ConversationService(db)
    topics = await service.get_topics()
    return ResponseBase(data={"topics": topics})

@router.get("/start", response_model=ResponseBase[ConversationStart])
async def start_conversation(db: AsyncSession = Depends(get_db)):
    service = ConversationService(db)
    result = await service.start_session()
    return ResponseBase(
        message="Ready",
        data=ConversationStart(topic=result["topic"], initial_question=result["message"])
    )

@router.post("/chat", response_model=ResponseBase[ChatResponse])
async def chat(
    input_data: ChatInput,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = ConversationService(db)
    talent_id = current_user["idtalent"]
    result = await service.process_chat(
        user_input=input_data.user_input,
        duration=input_data.duration,
        talent_id=talent_id,
        topic_id=input_data.topic_id
    )
    return ResponseBase(data=ChatResponse(**result))

@router.get("/report", response_model=ResponseBase)
async def get_conversation_report(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil report conversation terakhir yang REAL dari database user.
    """
    talent_id = current_user["idtalent"]
    
    query = select(Hasillatihanpercakapan).where(
        Hasillatihanpercakapan.idtalent == talent_id
    ).order_by(desc(Hasillatihanpercakapan.waktulatihan)).limit(1)
    
    result = await db.execute(query)
    last_session = result.scalar_one_or_none()
    
    if not last_session:
        return ResponseBase(success=False, message="No conversation history found")

    report_data = {
        "report": [
            {
                "wpm_confidence_info": f"WPM: {last_session.wpm} Confidence Score: {min(100, int(last_session.wpm))}",
                "grammar_issues": [
                    {
                        "message": last_session.grammar or "Good grammar usage.",
                        "suggestions": [],
                        "sentence": "Overall assessment"
                    }
                ]
            }
        ],
        "saveStatus": {
            "success": True, 
            "message": "Report generated from history", 
            "id": last_session.idhasilpercakapan
        },
        "talent_id": talent_id
    }
    
    return ResponseBase(data=report_data)