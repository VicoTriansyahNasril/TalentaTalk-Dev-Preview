from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

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
    Berisi informasi tambahan statistik.
    """
    total_phoneme_completed: int
    total_conversation_completed: int
    total_interview_completed: int
    last_activity_date: Optional[str] = None
    average_pronunciation_score: float = 0.0
    average_speaking_wpm: float = 0.0