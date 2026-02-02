from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.profile_service import ProfileService
from app.schemas.response import ResponseBase
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=ResponseBase)
async def get_profile_summary(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    data = await service.get_mobile_profile(current_user["idtalent"])
    return ResponseBase(data=data)