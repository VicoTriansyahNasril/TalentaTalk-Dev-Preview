from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PhonemeComparisonItem(BaseModel):
    target: str
    user: str
    status: str
    similarity: int

class PhonemeCheckResponse(BaseModel):
    similarity_percent: str
    accuracy_score: float
    target_phonemes: str
    user_phonemes: str
    phoneme_comparison: List[PhonemeComparisonItem]
    gemini_analysis: Optional[Dict[str, Any]] = None