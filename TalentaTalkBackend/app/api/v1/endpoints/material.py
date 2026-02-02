from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Path, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.material_service import MaterialService
from app.repositories.material_repository import MaterialRepository
from app.schemas.material import (
    PhonemeWordCreate, PhonemeWordUpdate,
    PhonemeSentenceCreate, PhonemeSentenceUpdate,
    ExamCreate, ExamUpdate,
    InterviewQuestionCreate, InterviewQuestionUpdate, InterviewQuestionResponse,
    SwapOrderRequest
)
from app.schemas.response import ResponseBase
from app.utils.time_utils import TimeUtils
from app.utils.template_generator import TemplateGenerator # Import baru
from app.api.deps import get_current_admin_user

router = APIRouter(dependencies=[Depends(get_current_admin_user)])

# --- TEMPLATE DOWNLOAD ENDPOINTS ---
@router.get("/phoneme-material/import-template")
async def get_word_template():
    buffer = TemplateGenerator.get_phoneme_word_template()
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=phoneme_word_template.xlsx"}
    )

@router.get("/exercise-phoneme/import-template")
async def get_sentence_template():
    buffer = TemplateGenerator.get_phoneme_sentence_template()
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=phoneme_sentence_template.xlsx"}
    )

@router.get("/exam-phoneme/import-template")
async def get_exam_template():
    buffer = TemplateGenerator.get_phoneme_exam_template()
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=phoneme_exam_template.xlsx"}
    )

# =======================
# PHONEME WORDS
# =======================
@router.post("/phoneme-material", response_model=ResponseBase)
async def add_word(request: PhonemeWordCreate, db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    data = {
        "kategori": request.phoneme_category, "kata": request.word,
        "meaning": request.meaning, "definition": request.word_definition,
        "fonem": request.phoneme
    }
    result = await repo.create_word(data)
    return ResponseBase(message="Word added", data={"id": result.idmaterifonemkata})

@router.put("/phoneme-material/words/{word_id}", response_model=ResponseBase)
async def update_word(word_id: int, request: PhonemeWordUpdate, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    # Mapping request ke DB column
    data = {}
    if request.word: data["kata"] = request.word
    if request.meaning: data["meaning"] = request.meaning
    if request.word_definition: data["definition"] = request.word_definition
    if request.phoneme: data["fonem"] = request.phoneme
    
    await service.update_word(word_id, data)
    return ResponseBase(message="Word updated")

@router.delete("/phoneme-material/words/{word_id}", response_model=ResponseBase)
async def delete_word(word_id: int, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    await service.delete_word(word_id)
    return ResponseBase(message="Word deleted")

# =======================
# PHONEME SENTENCES
# =======================
@router.post("/exercise-phoneme/sentences", response_model=ResponseBase)
async def add_sentence(request: PhonemeSentenceCreate, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    data = {
        "kategori": request.phoneme_category,
        "kalimat": request.sentence,
        "fonem": request.phoneme
    }
    result = await service.create_sentence(data)
    return ResponseBase(message="Sentence added", data={"id": result.idmaterifonemkalimat})

@router.put("/exercise-phoneme/sentences/{sentence_id}", response_model=ResponseBase)
async def update_sentence(sentence_id: int, request: PhonemeSentenceUpdate, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    data = {}
    if request.sentence: data["kalimat"] = request.sentence
    if request.phoneme: data["fonem"] = request.phoneme
    await service.update_sentence(sentence_id, data)
    return ResponseBase(message="Sentence updated")

@router.delete("/exercise-phoneme/sentences/{sentence_id}", response_model=ResponseBase)
async def delete_sentence(sentence_id: int, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    await service.delete_sentence(sentence_id)
    return ResponseBase(message="Sentence deleted")

# =======================
# EXAMS
# =======================
@router.post("/exam-phoneme/bulk-sentences", response_model=ResponseBase)
async def add_exam_bulk(request: ExamCreate, db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    service = MaterialService(repo)
    items_dict = [{"sentence": item.sentence, "phoneme": item.phoneme} for item in request.items]
    result = await service.create_exam(request.category, items_dict)
    return ResponseBase(message="Exam created", data={"examId": result.idmateriujian})

@router.put("/exam-phoneme/{phoneme_category}/tests/{test_id}", response_model=ResponseBase)
async def update_exam(phoneme_category: str, test_id: str, request: ExamUpdate, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    # Parse test_id (e.g. EXM001 -> 1)
    try:
        exam_id = int(test_id.replace("EXM", ""))
    except ValueError:
        exam_id = int(test_id)
        
    await service.update_exam_sentences(exam_id, request.sentences)
    return ResponseBase(message="Exam updated")

@router.delete("/exam-phoneme/{phoneme_category}/tests/{test_id}", response_model=ResponseBase)
async def delete_exam(phoneme_category: str, test_id: str, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    try:
        exam_id = int(test_id.replace("EXM", ""))
    except ValueError:
        exam_id = int(test_id)
    await service.delete_exam(exam_id)
    return ResponseBase(message="Exam deleted")

# =======================
# INTERVIEW QUESTIONS
# =======================
@router.get("/interview-questions", response_model=ResponseBase)
async def get_interview_questions(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    skip = (page - 1) * size
    questions = await repo.get_interview_questions(skip, size)
    
    data = [
        InterviewQuestionResponse(
            questionId=f"QST{q.idmateriinterview:03d}",
            interviewQuestion=q.question,
            isActive=q.is_active,
            createdAt=TimeUtils.format_to_wib(q.updated_at),
            orderPosition=idx + 1 + skip # approximate order
        ) for idx, q in enumerate(questions)
    ]
    return ResponseBase(data={"interviewQuestions": data})

@router.post("/interview-questions", response_model=ResponseBase)
async def add_interview_question(request: InterviewQuestionCreate, db: AsyncSession = Depends(get_db)):
    repo = MaterialRepository(db)
    result = await repo.create_interview_question(request.interview_question)
    return ResponseBase(status_code=status.HTTP_201_CREATED, message="Question added", data={"id": result.idmateriinterview})

@router.put("/interview-questions/{question_id}", response_model=ResponseBase)
async def update_interview_question(question_id: int, request: InterviewQuestionUpdate, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    await service.update_interview(question_id, request.interview_question)
    return ResponseBase(message="Question updated")

@router.delete("/interview-questions/{question_id}", response_model=ResponseBase)
async def delete_interview_question(question_id: int, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    await service.delete_interview(question_id)
    return ResponseBase(message="Question deleted")

@router.post("/interview-questions/{question_id}/toggle", response_model=ResponseBase)
async def toggle_interview_status(question_id: int, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    result = await service.toggle_interview(question_id)
    return ResponseBase(message="Status toggled", data={"isActive": result.is_active})

@router.post("/interview-questions/{question_id}/swap", response_model=ResponseBase)
async def swap_interview_order(question_id: int, request: SwapOrderRequest, db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    await service.swap_interview(question_id, request.direction)
    return ResponseBase(message=f"Swapped {request.direction}")

# =======================
# EXCEL IMPORTS
# =======================
@router.post("/phoneme-material/import", response_model=ResponseBase)
async def import_words(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    content = await file.read()
    result = await service.import_words_from_excel(content)
    return ResponseBase(message="Import completed", data=result)

@router.post("/exercise-phoneme/import", response_model=ResponseBase)
async def import_sentences(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    content = await file.read()
    result = await service.import_sentences_from_excel(content)
    return ResponseBase(message="Import completed", data=result)

@router.post("/exam-phoneme/import", response_model=ResponseBase)
async def import_exams(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    service = MaterialService(MaterialRepository(db))
    content = await file.read()
    result = await service.import_exams_from_excel(content)
    return ResponseBase(message="Import completed", data=result)