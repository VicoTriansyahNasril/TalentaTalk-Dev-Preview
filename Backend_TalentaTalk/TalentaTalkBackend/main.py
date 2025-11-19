# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from view.AuthView import authrouter
from view.ConversationOllamaView import conversationrouter
from view.InterviewOllamaView import interviewrouter as interviewollamarouter
from view.PhonemeRecognitionView import phonemerecognitionrouter
from view.HomeView import homerouter
from view.ExamView import examrouter
from view.TranscribeView import transcriberouter
from view.PronunciationMaterial import pronunciationmaterialrouter
from view.TalentListView import talentlistrouter
from view.InterviewMaterialView import interviewrouter as interviewmaterialrouter
from view.ExamPhonemeView import examphonemematerialrouter  
from view.ProfileView import profilerouter
from view.HistoryView import historyrouter
from view.HomeMobileView import homeactivityrouter
from view.PretestView import pretestrouter
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()

# ✅ CORS configuration with multiple origins
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server  
    "https://talentatalk.cloudias79.com",  # Production frontend
    "http://talentatalk.cloudias79.com",   # HTTP fallback
]

# Tambah origins dari environment variable jika ada
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    additional_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    allowed_origins.extend(additional_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="secret-session-a8f6a98e0ae3fcc362054e3143ebc525fe4ba938bcd430620706f3d814937df4")

app.include_router(homerouter)
app.include_router(authrouter)
app.include_router(conversationrouter)
app.include_router(interviewmaterialrouter)
app.include_router(interviewollamarouter)
app.include_router(phonemerecognitionrouter)
app.include_router(examrouter)
app.include_router(transcriberouter)
app.include_router(talentlistrouter)
app.include_router(pronunciationmaterialrouter)
app.include_router(profilerouter)
app.include_router(historyrouter)
app.include_router(homeactivityrouter)
app.include_router(examphonemematerialrouter)
app.include_router(pretestrouter)