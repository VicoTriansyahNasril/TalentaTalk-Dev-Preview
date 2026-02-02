from fastapi import APIRouter, Depends, UploadFile, File, Form, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.material_repository import MaterialRepository
from app.repositories.talent_repository import TalentRepository
from app.services.phoneme_service import PhonemeService
from app.services.audio_service import AudioService
from app.utils.phoneme_utils import PhonemeMatcher
from app.schemas.response import ResponseBase
from app.api.deps import get_current_user
from app.models.models import Talent

router = APIRouter()

@router.get("/check", response_model=ResponseBase)
async def check_onboarding(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cek apakah user sudah pretest"""
    talent_repo = TalentRepository(db)
    talent = await talent_repo.get_by_id(current_user["idtalent"])
    show_onboarding = talent.pretest_score is None if talent else False
    return ResponseBase(data={"show_onboarding": show_onboarding})

@router.get("/start", response_model=ResponseBase)
async def start_pretest(db: AsyncSession = Depends(get_db)):
    """Ambil 10 soal acak untuk pretest"""
    repo = MaterialRepository(db)
    questions = await repo.get_random_sentences(limit=10)
    data = [
        {
            "id": q.idmaterifonemkalimat,
            "kategori": q.kategori,
            "kalimat": q.kalimat,
            "fonem": q.fonem
        } for q in questions
    ]
    return ResponseBase(data=data)

@router.post("/compare", response_model=ResponseBase)
async def compare_pretest(
    idContent: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Analisis audio pretest (tanpa simpan ke DB history, hanya return score)"""
    repo = MaterialRepository(db)
    content = await repo.get_phoneme_content(idContent, "sentence")
    if not content: return ResponseBase(success=False, message="Content not found")
    
    audio_bytes = await file.read()
    user_phonemes = await AudioService.transcribe(audio_bytes)
    alignment = PhonemeMatcher.align_phonemes(content.fonem, user_phonemes)
    score = PhonemeMatcher.calculate_accuracy(alignment)
    
    return ResponseBase(data={
        "similarity_percent": f"{score}%",
        "phoneme_comparison": alignment,
        "user_phonemes": user_phonemes,
        "target_phonemes": content.fonem
    })

@router.post("/submit", response_model=ResponseBase)
async def submit_pretest(
    payload: dict, # {"score": float}
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Simpan nilai akhir pretest ke profil talent"""
    talent_repo = TalentRepository(db)
    talent = await talent_repo.get_by_id(current_user["idtalent"])
    if talent:
        await talent_repo.update(talent, {"pretest_score": payload.get("score", 0)})
        return ResponseBase(message="Pretest score saved")
    return ResponseBase(success=False, message="Talent not found")