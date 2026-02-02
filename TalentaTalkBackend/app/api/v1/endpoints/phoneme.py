from fastapi import APIRouter, Depends, UploadFile, File, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.phoneme_service import PhonemeService
from app.repositories.material_repository import MaterialRepository
from app.repositories.score_repository import ScoreRepository
from app.schemas.response import ResponseBase
from app.schemas.phoneme import PhonemeCheckResponse

router = APIRouter()

@router.post("/compare", response_model=ResponseBase[PhonemeCheckResponse])
async def compare_phonemes(
    idContent: int = Form(...),
    type: str = Form("sentence"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    talent_id = 1 # TODO: Auth
    mat_repo = MaterialRepository(db)
    score_repo = ScoreRepository(db)
    service = PhonemeService(mat_repo, score_repo)

    audio_content = await file.read()
    result = await service.process_pronunciation(talent_id, idContent, audio_content, type)
    return ResponseBase(message="Analysis completed", data=PhonemeCheckResponse(**result))

@router.post("/compare_word", response_model=ResponseBase[PhonemeCheckResponse])
async def compare_phonemes_word(
    idContent: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Alias khusus untuk compare word (mobile legacy)"""
    return await compare_phonemes(idContent=idContent, type="word", file=file, db=db)

# --- MISSING ENDPOINTS RESTORED ---

@router.get("/word_by_id/{id}", response_model=ResponseBase)
async def get_word_by_id(id: int, db: AsyncSession = Depends(get_db)):
    mat_repo = MaterialRepository(db)
    score_repo = ScoreRepository(db)
    service = PhonemeService(mat_repo, score_repo)
    data = await service.get_word_by_id(id)
    return ResponseBase(data=data)

@router.get("/sentence_by_id/{id}", response_model=ResponseBase)
async def get_sentence_by_id(id: int, db: AsyncSession = Depends(get_db)):
    mat_repo = MaterialRepository(db)
    score_repo = ScoreRepository(db)
    service = PhonemeService(mat_repo, score_repo)
    data = await service.get_sentence_by_id(id)
    return ResponseBase(data=data)

@router.get("/random_word/{phoneme}", response_model=ResponseBase)
async def get_random_word(phoneme: str, db: AsyncSession = Depends(get_db)):
    mat_repo = MaterialRepository(db)
    score_repo = ScoreRepository(db)
    service = PhonemeService(mat_repo, score_repo)
    data = await service.get_random_word(phoneme)
    if not data: return ResponseBase(success=False, message="No data found")
    return ResponseBase(data=data)

@router.get("/random_sentence/{phoneme}", response_model=ResponseBase)
async def get_random_sentence(phoneme: str, db: AsyncSession = Depends(get_db)):
    mat_repo = MaterialRepository(db)
    score_repo = ScoreRepository(db)
    service = PhonemeService(mat_repo, score_repo)
    data = await service.get_random_sentence(phoneme)
    if not data: return ResponseBase(success=False, message="No data found")
    return ResponseBase(data=data)

# --- CATEGORY LISTS (Mobile) ---
@router.get("/phoneme_words_categories", response_model=ResponseBase)
async def get_word_categories(db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    categories = await repo.get_all_word_categories()
    return ResponseBase(data={"categories": categories})

@router.get("/phoneme_sentences_categories", response_model=ResponseBase)
async def get_sentence_categories(db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    categories = await repo.get_all_sentence_categories()
    return ResponseBase(data={"categories": categories})

@router.get("/words_by_category/{category}", response_model=ResponseBase)
async def get_words_by_category(category: str, db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    words = await repo.get_words_by_category(category)
    data = [{
        "idContent": w.idmaterifonemkata, "content": w.kata, 
        "phoneme": w.fonem, "phoneme_category": w.kategori
    } for w in words]
    return ResponseBase(data={"category": category, "words": data})

@router.get("/sentences_by_category/{category}", response_model=ResponseBase)
async def get_sentences_by_category(category: str, db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    sentences = await repo.get_sentences_by_category(category)
    data = [{
        "idContent": s.idmaterifonemkalimat, "content": s.kalimat, 
        "phoneme": s.fonem, "phoneme_category": s.kategori
    } for s in sentences]
    return ResponseBase(data={"category": category, "sentences": data})