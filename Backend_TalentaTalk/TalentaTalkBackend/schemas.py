#schemas.py
from pydantic import BaseModel, EmailStr, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from config.phoneme_constants import PhonemeConstants

def validate_is_not_empty_string(v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Field cannot be empty')
    return v.strip()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class CreateTalentRequest(BaseModel):
    email: EmailStr
    password: str
    nama: str
    role: Optional[str] = None

    @validator('password')
    def validate_password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('nama')
    def validate_nama(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama tidak boleh kosong')
        return v.strip()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class ChatInput(BaseModel):
    user_input: str
    duration: str  # format mm:ss

class StartResponse(BaseModel):
    message: str
    topic: str

class ChatResponse(BaseModel):
    response: str
    confidence_score: int
    grammar_check: str
    # history: List[dict]

class GrammarIssue(BaseModel):
    message: str
    suggestions: List[str]
    sentence: str

class ReportItem(BaseModel):
    user_input: str
    wpm_confidence_info: str
    grammar_issues: List[GrammarIssue]

class ReportResponse(BaseModel):
    report: List[ReportItem]

class SaveStatus(BaseModel):
    success: bool
    message: str
    
class SaveReportResponse(BaseModel):
    report: List[ReportItem]
    save_status: SaveStatus

class TalentRequest(BaseModel):
    talent_id: int

class SaveReportRequest(BaseModel):
    talent_id: int
    topic: str
    confidence_report: List[Dict[str, str]]
    
class AnswerRequest(BaseModel):
    answer: str
    duration: str

class SummaryRequest(BaseModel):
    talent_id: int

class PretestScoreRequest(BaseModel):
    score: float

class InterviewSummaryResponse(BaseModel):
    success: bool
    summary: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    id: Optional[int] = None

class InterviewResponse(BaseModel):
    status: str
    feedback: Optional[str] = None
    message: str
    interview_completed: bool

class AddMaterialRequest(BaseModel):
    phoneme_category: str
    word: str
    meaning: str
    word_definition: str
    phoneme: str

    @validator('phoneme_category')
    def validate_phoneme_category(cls, v):
        if not PhonemeConstants.is_valid_phoneme(v):
            raise ValueError(f'Invalid phoneme category: {v}. Must be a single phoneme like: i, ɪ, p, b')
        return v

    _validate_word = validator('word', allow_reuse=True)(validate_is_not_empty_string)
    _validate_meaning = validator('meaning', allow_reuse=True)(validate_is_not_empty_string)
    _validate_phoneme = validator('phoneme', allow_reuse=True)(validate_is_not_empty_string)

class AddSentenceRequest(BaseModel):
    phoneme_category: str
    sentence: str
    phoneme: str

    @validator('sentence')
    def validate_sentence_length(cls, v):
        if len(v.split()) < 4:
            raise ValueError('Sentence must contain at least 4 words')
        return v

    @validator('phoneme_category')
    def validate_phoneme_category(cls, v):
        if not PhonemeConstants.validate_minimal_pair_category(v) or "-" not in v:
            raise ValueError(f'Invalid category: {v}. Must be minimal pairs like: i-ɪ, p-b, s-z')
        return v

    _validate_phoneme = validator('phoneme', allow_reuse=True)(validate_is_not_empty_string)

class SentencePhonemePair(BaseModel):
    sentence: str
    phoneme: str

    @validator('sentence')
    def validate_sentence_length(cls, v):
        if len(v.split()) < 10:
            raise ValueError('Sentence must contain at least 10 words')
        return v

    _validate_phoneme = validator('phoneme', allow_reuse=True)(validate_is_not_empty_string)

class AddExamSentenceRequest(BaseModel):
    category: str
    items: List[SentencePhonemePair]

    @validator('items')
    def validate_sentence_count(cls, v):
        if len(v) != 10:
            raise ValueError('Each exam must have exactly 10 sentences')
        return v

    @validator('category')
    def validate_phoneme_category(cls, v):
        if '-' not in v:
            raise ValueError(f'Category must be minimal pairs (e.g., i-ɪ, p-b, s-z), got: {v}')
        if not PhonemeConstants.validate_minimal_pair_category(v):
            raise ValueError(f'Invalid minimal pair category: {v}')
        return v

class UpdateSentenceRequest(BaseModel):
    id_sentence: int
    sentence: str
    phoneme: str

    @validator('sentence')
    def validate_sentence_length(cls, v):
        if len(v.split()) < 10:
            raise ValueError('Sentence must contain at least 10 words')
        return v

    _validate_phoneme = validator('phoneme', allow_reuse=True)(validate_is_not_empty_string)

class UpdateExamDetailRequest(BaseModel):
    sentences: List[UpdateSentenceRequest]

class AddInterviewMaterialRequest(BaseModel):
    interview_question: str

    @validator('interview_question')
    def validate_question_length(cls, v):
        if len(v.split()) < 5:
            raise ValueError('Interview question must contain at least 5 words')
        return v

class UpdateAdminProfileRequest(BaseModel):
    nama: str
    email: str

    @validator('email')
    def validate_email_format(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

    @validator('nama')
    def validate_nama(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama tidak boleh kosong')
        return v.strip()
    
class ChangePasswordRequest(BaseModel):
    new_password: str
    confirm_password: Optional[str] = None

    @validator('new_password')
    def validate_password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password minimal 6 karakter')
        return v

class PaginationParams(BaseModel):
    search: Optional[str] = None
    page: int = 1
    size: int = 10

    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            return 1
        return v

    @validator('size')
    def validate_size(cls, v):
        if v not in [10, 25, 50]:
            return 10
        return v

class UpdateTalentRequest(BaseModel):
    nama: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

    @validator('nama')
    def validate_nama(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Nama tidak boleh kosong')
        return v.strip() if v else v

    @validator('email')
    def validate_email_format(cls, v):
        if v is not None:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Format email tidak valid')
        return v