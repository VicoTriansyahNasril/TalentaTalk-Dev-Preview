from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import ChatInput, ChatResponse, ConversationStart
from app.schemas.response import ResponseBase
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/start", response_model=ResponseBase[ConversationStart])
async def start_conversation(
    db: AsyncSession = Depends(get_db)
):
    """
    Memulai sesi percakapan baru.
    Service akan memilih topik acak dan generate pertanyaan pembuka via AI.
    """
    service = ConversationService(db)
    result = await service.start_session()
    
    return ResponseBase(
        message="Conversation started",
        data=ConversationStart(
            topic=result["topic"], 
            initial_question=result["message"]
        )
    )

@router.post("/chat", response_model=ResponseBase[ChatResponse])
async def chat(
    input_data: ChatInput,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Memproses chat user.
    """
    service = ConversationService(db)
    
    talent_id = current_user["idtalent"]
    
    result = await service.process_chat(
        user_input=input_data.user_input,
        duration=input_data.duration,
        talent_id=talent_id,
        topic_id=1
    )
    
    return ResponseBase(data=ChatResponse(**result))