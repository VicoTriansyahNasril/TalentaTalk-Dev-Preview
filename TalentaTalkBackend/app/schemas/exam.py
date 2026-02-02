from pydantic import BaseModel
from typing import List, Optional, Any

class ExamStartResponse(BaseModel):
    id_ujianfonem: int
    remaining: int
    data: List[dict]

class ExamResultDetail(BaseModel):
    idsoal: int
    kalimat: str
    nilai: float

class ExamResultResponse(BaseModel):
    success: bool
    id_ujian: int
    kategori: str
    jumlah_soal: int
    nilai_rata_rata: float
    detail: List[ExamResultDetail]