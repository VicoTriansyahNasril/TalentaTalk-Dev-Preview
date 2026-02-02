from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.database import engine, Base
from app.api.v1.endpoints import (
    auth, conversation, phoneme, dashboard, material, 
    talents, history, exam, transcribe, interview_flow, mobile_profile, pretest
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": str(exc.detail), "data": None},
    )

# --- WEB ADMIN ---
app.include_router(auth.router, prefix="/web/admin", tags=["Auth Admin"])
app.include_router(dashboard.router, prefix="/web/admin", tags=["Dashboard"])
app.include_router(material.router, prefix="/web/admin", tags=["Material"])
app.include_router(talents.router, prefix="/web/admin/talents", tags=["Talent Management"])

# --- MOBILE APP ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth Mobile"])
app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["Conversation"])
app.include_router(interview_flow.router, prefix="/api/v1/interview", tags=["Interview"])
app.include_router(phoneme.router, prefix="/api/v1/phoneme", tags=["Phoneme"])
app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
app.include_router(exam.router, prefix="/api/v1/exam", tags=["Exam"])
app.include_router(transcribe.router, prefix="/api/v1", tags=["Transcribe"])
app.include_router(mobile_profile.router, prefix="/api/v1/profile", tags=["Profile Mobile"])
app.include_router(pretest.router, prefix="/api/v1/pretest", tags=["Pretest"])

@app.get("/")
def root():
    return {"message": "TalentaTalk API v1.6 Running"}