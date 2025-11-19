# routers/profile_router.py

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from controller.ProfileController import get_profile_summary
from controller.AuthController import get_current_user

profilerouter = APIRouter(prefix="/profile", tags=["Profile"])

@profilerouter.get("/summary")
async def get_profile_summary_route(authorization: str = Header(None), db: Session = Depends(get_db)):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]
    return get_profile_summary(db, idtalent)
