from pydantic import BaseModel, Field
from typing import List, Optional

# --- Shared ---
class SwapOrderRequest(BaseModel):
    direction: str = Field(..., pattern="^(up|down)$")

# --- Word Material ---
class PhonemeWordCreate(BaseModel):
    phoneme_category: str
    word: str
    meaning: str
    word_definition: Optional[str] = ""
    phoneme: str

class PhonemeWordUpdate(BaseModel):
    word: Optional[str] = None
    meaning: Optional[str] = None
    word_definition: Optional[str] = None
    phoneme: Optional[str] = None

# --- Sentence Exercise ---
class PhonemeSentenceCreate(BaseModel):
    phoneme_category: str
    sentence: str = Field(..., min_length=10)
    phoneme: str

class PhonemeSentenceUpdate(BaseModel):
    sentence: Optional[str] = None
    phoneme: Optional[str] = None

# --- Exam ---
class ExamSentenceItem(BaseModel):
    id_sentence: int
    sentence: str
    phoneme: str

class ExamCreate(BaseModel):
    category: str
    items: List[ExamSentenceItem]

class ExamUpdate(BaseModel):
    sentences: List[ExamSentenceItem]

# --- Interview ---
class InterviewQuestionCreate(BaseModel):
    interview_question: str = Field(..., min_length=5)

class InterviewQuestionUpdate(BaseModel):
    interview_question: str = Field(..., min_length=5)

class InterviewQuestionResponse(BaseModel):
    questionId: str
    interviewQuestion: str
    isActive: bool
    createdAt: str
    orderPosition: int