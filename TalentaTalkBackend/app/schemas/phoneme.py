from pydantic import BaseModel
from typing import List, Optional

class PhonemeComparisonItem(BaseModel):
    target: str
    user: str
    status: str
    similarity: int

class PhonemeResponse(BaseModel):
    similarity_percent: str
    target_phonemes: str
    user_phonemes: str
    phoneme_comparison: List[PhonemeComparisonItem]
    accuracy_score: float