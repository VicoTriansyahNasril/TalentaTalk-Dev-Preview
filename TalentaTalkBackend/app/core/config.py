import os
from typing import List, Dict, Any
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentaTalk API"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # DATABASE
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "appdb")
    
    # Konstruksi URL Database (Computed)
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # AI CONFIG (Dinamis)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_ID: str = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash")
    
    @property
    def GEMINI_API_URL(self) -> str:
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.GEMINI_MODEL_ID}:generateContent"

    # CORS (Support Local & Production via Env)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    # PHONETIC CONSTANTS (Static Logic)
    TIE_BAR_NORMALIZATION: Dict[str, str] = {
        "d͡ʒ": "dʒ", "t͡ʃ": "tʃ", "t͡s": "ts", "d͡z": "dz"
    }

    SIMILAR_PHONEMES: Dict[str, List[str]] = {
        "i": ["ɪ", "j"], "ɪ": ["ɛ"], "ɛ": ["æ"], "u": ["ʊ", "w"],
        "p": ["b"], "t": ["d"], "k": ["g"], "f": ["v"],
        "θ": ["ð"], "s": ["z"], "ʃ": ["ʒ"], "tʃ": ["dʒ"],
        "n": ["m", "ŋ"], "l": ["r"], "ə": ["ʌ", "ɚ"],
        "ɑ": ["ɔ", "ʌ"], "ɔ": ["oʊ"], "oʊ": ["ʊ"],
        "eɪ": ["ɛ", "ɪ"], "aɪ": ["ɪ", "ɑ"], "ɔɪ": ["ɔ", "ɪ"],
        "aʊ": ["ʊ", "ɑ"],
    }
    
    VOWEL_PHONEMES: List[str] = ["i", "ɪ", "ɛ", "æ", "ə", "ɚ", "ʌ", "ɑ", "ɔ", "ʊ", "u"]
    DIPHTHONG_PHONEMES: List[str] = ["eɪ", "aɪ", "ɔɪ", "aʊ", "oʊ"]
    CONSONANT_PHONEMES: List[str] = ["p", "b", "t", "d", "k", "g", "f", "v", "θ", "ð", "s", "z", "ʃ", "ʒ", "tʃ", "dʒ", "h", "m", "n", "ŋ", "l", "r", "j", "w"]

    @field_validator("SECRET_KEY", "GEMINI_API_KEY", "DB_PASSWORD")
    def check_empty_secrets(cls, v, info):
        if not v:
            raise ValueError(f"CRITICAL: {info.field_name} must be set in .env")
        return v

    class Config:
        case_sensitive = True

settings = Settings()