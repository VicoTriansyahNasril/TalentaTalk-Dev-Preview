from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List

# --- READ SCHEMAS (OUTPUT) ---

class TalentDTO(BaseModel):
    id: int
    talentName: str = Field(alias="nama")
    email: EmailStr
    role: str
    pretest: str
    highestExam: str
    progress: str

    class Config:
        from_attributes = True
        populate_by_name = True

class TalentDetailDTO(TalentDTO):
    """
    Schema lengkap untuk detail page talent.
    """
    total_phoneme_completed: int
    total_conversation_completed: int
    total_interview_completed: int
    last_activity_date: Optional[str] = None
    average_pronunciation_score: float = 0.0
    average_speaking_wpm: float = 0.0

# --- WRITE SCHEMAS (INPUT) ---

class TalentUpdate(BaseModel):
    """
    Schema untuk update data profile talent (Nama, Email, Role).
    Semua field optional agar bisa update parsial.
    """
    nama: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

    @validator('nama')
    def validate_nama(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Nama tidak boleh kosong')
        return v.strip() if v else v

class TalentPasswordUpdate(BaseModel):
    """
    Schema khusus untuk ganti password talent.
    """
    new_password: str = Field(..., min_length=6, description="Password minimal 6 karakter")