from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.talent_service import TalentService
from app.schemas.talent import TalentUpdate
from app.schemas.response import ResponseBase
from app.utils.template_generator import TemplateGenerator
from app.api.deps import get_current_admin_user

router = APIRouter(dependencies=[Depends(get_current_admin_user)])

@router.get("", response_model=ResponseBase)
async def get_talent_list(
    searchQuery: str = Query(None), page: int = Query(1, ge=1), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)
):
    service = TalentService(db)
    result = await service.get_talents_list(page, limit, searchQuery)
    pagination = {"currentPage": result["page"], "totalRecords": result["total"], "totalPages": (result["total"] + limit - 1) // limit}
    return ResponseBase(data={"talents": result["data"], "pagination": pagination}, message="Data talent berhasil diambil")

@router.get("/import-template")
async def get_talent_template():
    buffer = TemplateGenerator.get_talent_template()
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=talent_import_template.xlsx"})

@router.post("/import", response_model=ResponseBase)
async def import_talents(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    content = await file.read()
    result = await service.import_talents_from_excel(content)
    return ResponseBase(message="Talent import completed", data=result)

@router.get("/{talent_id}", response_model=ResponseBase)
async def get_talent_detail(talent_id: int, db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    data = await service.get_talent_detail(talent_id)
    return ResponseBase(data=data)

@router.put("/{talent_id}", response_model=ResponseBase)
async def update_talent(talent_id: int, request: TalentUpdate, db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    await service.update_talent(talent_id, request)
    return ResponseBase(message="Data talent berhasil diperbarui")

@router.delete("/{talent_id}", response_model=ResponseBase)
async def delete_talent(talent_id: int, db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    await service.delete_talent(talent_id)
    return ResponseBase(message="Talent berhasil dihapus")

@router.put("/{talent_id}/change-password", response_model=ResponseBase)
async def change_talent_password(talent_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    await service.change_password(talent_id, payload.get("new_password"))
    return ResponseBase(message="Password berhasil diubah")

@router.get("/{talent_id}/phoneme-material-exercise", response_model=ResponseBase)
async def get_phoneme_word_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    result = await service.get_phoneme_progress(talent_id, "Word", page, limit)
    return ResponseBase(data={"phonemeCategories": result["data"], "pagination": {"currentPage": page, "totalRecords": result["total"], "totalPages": (result["total"] + limit - 1) // limit}})

@router.get("/{talent_id}/phoneme-exercise", response_model=ResponseBase)
async def get_phoneme_sentence_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    result = await service.get_phoneme_progress(talent_id, "Sentence", page, limit)
    return ResponseBase(data={"phonemeExercises": result["data"], "pagination": {"currentPage": page, "totalRecords": result["total"], "totalPages": (result["total"] + limit - 1) // limit}})

@router.get("/{talent_id}/phoneme-exam", response_model=ResponseBase)
async def get_phoneme_exam_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    result = await service.get_exam_progress(talent_id, page, limit)
    return ResponseBase(data={"phonemeExams": result["data"], "pagination": {"currentPage": page, "totalRecords": result["total"], "totalPages": (result["total"] + limit - 1) // limit}})

@router.get("/{talent_id}/phoneme-exam/attempt/{attempt_id}/detail", response_model=ResponseBase)
async def get_exam_attempt_detail(talent_id: int, attempt_id: int, db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    data = await service.get_exam_attempt_detail(talent_id, attempt_id)
    return ResponseBase(data={"examAttemptDetail": data})

@router.get("/{talent_id}/conversation", response_model=ResponseBase)
async def get_conversation_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    result = await service.get_conversation_progress(talent_id, page, limit)
    return ResponseBase(data={"conversations": result["data"], "pagination": {"currentPage": page, "totalRecords": result["total"], "totalPages": (result["total"] + limit - 1) // limit}})

@router.get("/{talent_id}/interview", response_model=ResponseBase)
async def get_interview_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1), db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    result = await service.get_interview_progress(talent_id, page, limit)
    return ResponseBase(data={"interviews": result["data"], "pagination": {"currentPage": page, "totalRecords": result["total"], "totalPages": (result["total"] + limit - 1) // limit}})

@router.get("/{talent_id}/interview/{attempt_id}/detail", response_model=ResponseBase)
async def get_interview_detail(talent_id: int, attempt_id: int, db: AsyncSession = Depends(get_db)):
    service = TalentService(db)
    data = await service.get_interview_detail(talent_id, attempt_id)
    return ResponseBase(data={"interviewDetail": data})