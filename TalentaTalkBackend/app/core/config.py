import os
from typing import List, Optional, Dict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentaTalk API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-session-a8f6a98e0ae3fcc362054e3143ebc525fe4ba938bcd430620706f3d814937df4")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Database
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "appdb")
    
    SQLALCHEMY_DATABASE_URI: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # AI Config
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://talentatalk.cloudias79.com",
        "http://talentatalk.cloudias79.com",
        "*"
    ]

    # --- PHONEME DATA (FULL) ---
    SIMILAR_PHONEMES: Dict[str, List[str]] = {
        "i": ["ɪ", "j"],
        "ɪ": ["ɛ"],
        "ɛ": ["æ"],
        "u": ["ʊ", "w"],
        "p": ["b"],
        "t": ["d"],
        "k": ["g"],
        "f": ["v"],
        "θ": ["ð"],
        "s": ["z"],
        "ʃ": ["ʒ"],
        "tʃ": ["dʒ"],
        "n": ["m", "ŋ"],
        "l": ["r"],
        "ə": ["ʌ", "ɚ"],
        "ɑ": ["ɔ", "ʌ"],
        "ɔ": ["oʊ"],
        "oʊ": ["ʊ"],
        "eɪ": ["ɛ", "ɪ"],
        "aɪ": ["ɪ", "ɑ"],
        "ɔɪ": ["ɔ", "ɪ"],
        "aʊ": ["ʊ", "ɑ"],
    }
    
    VOWEL_PHONEMES: List[str] = [
        "i", "ɪ", "ɛ", "æ", "ə", "ɚ", "ʌ", "ɑ", "ɔ", "ʊ", "u"
    ]
    
    DIPHTHONG_PHONEMES: List[str] = [
        "eɪ", "aɪ", "ɔɪ", "aʊ", "oʊ"
    ]
    
    CONSONANT_PHONEMES: List[str] = [
        "p", "b", "t", "d", "k", "g", "f", "v", "θ", "ð",
        "s", "z", "ʃ", "ʒ", "tʃ", "dʒ", "h", "m", "n", "ŋ", "l", "r", "j", "w"
    ]

    class Config:
        case_sensitive = True

settings = Settings()