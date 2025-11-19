# view/PronunciationMaterial.py

from fastapi import APIRouter, Body, Depends, File, Path, Query, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from utils.timestamp_helper import TimestampHelper
from controller.AuthController import get_current_admin_user
from controller.PronunciationMaterialController import PronunciationMaterialController
from database import get_db
from schemas import (
    AddMaterialRequest, AddSentenceRequest, AddExamSentenceRequest,
    AddInterviewMaterialRequest, UpdateExamDetailRequest, UpdateSentenceRequest
)
from utils.response_formatter import APIResponse
from utils.template_generator import TemplateGenerator
from config.phoneme_constants import MaterialType

pronunciationmaterialrouter = APIRouter(
    prefix="/web/admin",
    dependencies=[Depends(get_current_admin_user)]
)

# ================================
# PHONEME MATERIAL ENDPOINTS (KATA)
# ================================

@pronunciationmaterialrouter.get("/phoneme-material")
def get_phoneme_materials(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Pronunciation Material Management - Phoneme Material List"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_phoneme_materials(search, page, limit)

        phoneme_materials = []
        for material in result["data"]:
            phoneme_materials.append({
                "phoneme": material["phoneme"],
                "phonemeCategory": material["phoneme"],
                "totalWords": material["totalWords"],
                "lastUpdate": material["last_update"]
            })
        
        return APIResponse.success(
            data={
                "phonemeMaterials": phoneme_materials,
                "pagination": result.get("pagination", {})
            },
            message="Data phoneme material berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@pronunciationmaterialrouter.get("/phoneme-material/import-template")
def get_phoneme_material_template():
    """Get import template for phoneme material - RETURNS EXCEL FILE"""
    try:
        template_data = TemplateGenerator.get_template_by_type(MaterialType.WORD)
        buffer = TemplateGenerator.create_excel_buffer(template_data)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=\"phoneme_material_template.xlsx\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@pronunciationmaterialrouter.post("/phoneme-material")
def add_phoneme_material(
    request: AddMaterialRequest,
    db: Session = Depends(get_db)
):
    """Add New Material Modal"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.add_phoneme_word(
            request.phoneme_category,
            request.word,
            request.meaning,
            request.word_definition,
            request.phoneme
        )
        
        response_data = {
            "materialId": f"MAT{result['data']['id']:03d}",
            "phonemeCategory": result['data']['category'],
            "words": [result['data']['word']],
            "wordMeaning": result['data']['meaning'],
            "wordDefinition": result['data']['definition'],
            "createdAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Material phoneme berhasil ditambahkan",
            status_code=status.HTTP_201_CREATED
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_400_BAD_REQUEST and "already exists" in str(e.detail):
            return APIResponse.error(
                message="Kategori phoneme sudah ada",
                status_code=status.HTTP_409_CONFLICT
            )
        if "Invalid phoneme" in str(e.detail):
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.post("/phoneme-material/import")
def import_phoneme_material(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Phoneme Material Modal - ENHANCED VERSION"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.import_phoneme_word_from_excel(file)
        
        response_data = {
            "totalProcessed": result['total_processed'],
            "successCount": result['success_count'],
            "errorCount": result['error_count'],
            "errors": [
                {
                    "row": error["row"],
                    "error": error["reason"]
                } for error in result.get('skipped', [])
            ]
        }
        
        if result['success_count'] > 0:
            message = f"Import berhasil: {result['success_count']} material ditambahkan"
            if result['error_count'] > 0:
                message += f", {result['error_count']} error"
        else:
            message = f"Import gagal: {result['error_count']} error ditemukan"
        
        return APIResponse.success(
            data=response_data,
            message=message
        )
        
    except HTTPException as e:
        return APIResponse.error(
            message=str(e.detail),
            status_code=e.status_code
        )
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan saat import file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.get("/phoneme-material/{phoneme_category:path}/detail")
def get_phoneme_material_detail(
    phoneme_category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Phoneme Material Detail (Words by Category)"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_phoneme_words_by_category(phoneme_category, page, limit)
        
        return APIResponse.success(
            data=result,
            message="Detail phoneme material berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.put("/phoneme-material/{phoneme_category}/words/{word_id}")
def update_phoneme_material_word(
    phoneme_category: str,
    word_id: int,
    request: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Edit Material Modal"""
    try:
        if not all(key in request for key in ["word", "wordMeaning"]):
            return APIResponse.error(
                message="Word and wordMeaning are required fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        controller = PronunciationMaterialController(db)
        
        existing_words = controller.get_phoneme_words_by_category(phoneme_category, 1, 1000)
        for existing_word in existing_words.get("data", []):
            if existing_word["word"] == request["word"] and existing_word["id"] != word_id:
                return APIResponse.error(
                    message="Kata sudah ada dalam kategori ini",
                    status_code=status.HTTP_409_CONFLICT
                )
                
        update_payload = {
            "kata": request["word"],
            "meaning": request["wordMeaning"],
            "definition": request.get("wordDefinition", ""),
            "fonem": request.get("phoneme", phoneme_category)
        }
        
        result = controller.update_phoneme_word(word_id, update_payload)
        
        response_data = {
            "wordId": f"WRD{word_id:03d}",
            "word": request["word"],
            "wordMeaning": request["wordMeaning"],
            "wordDefinition": request.get("wordDefinition", ""),
            "phoneme": request.get("phoneme", phoneme_category),
            "updatedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Material kata berhasil diperbarui"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Kata tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        if "Invalid phoneme" in str(e.detail):
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.delete("/phoneme-material/words/{word_id}")
def delete_phoneme_material_word(
    word_id: int,
    db: Session = Depends(get_db)
):
    """Delete word dari phoneme material"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.delete_phoneme_word(word_id)
        
        response_data = {
            "wordId": f"WRD{word_id:03d}",
            "deletedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Kata berhasil dihapus"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Kata tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# EXERCISE PHONEME ENDPOINTS (KALIMAT)
# ================================

@pronunciationmaterialrouter.get("/exercise-phoneme")
def get_exercise_phoneme(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Exercise Phoneme Management"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_exercise_phoneme(search, page, limit)
        
        exercise_phonemes = []
        for exercise in result["data"]:
            exercise_phonemes.append({
                "phonemeCategory": exercise["phoneme_category"],
                "totalSentence": exercise["totalSentence"],
                "lastUpdate": exercise["last_update"]
            })
        
        return APIResponse.success(
            data={
                "exercisePhonemes": exercise_phonemes,
                "pagination": result.get("pagination", {})
            },
            message="Data exercise phoneme berhasil diambil"
        )
        
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.post("/exercise-phoneme/sentences")
def add_exercise_sentence(
    request: AddSentenceRequest,
    db: Session = Depends(get_db)
):
    """Add New Exercise Sentence Modal"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.add_phoneme_sentence(
            request.phoneme_category,
            request.sentence,
            request.phoneme
        )
        
        response_data = {
            "sentenceId": f"SEN{result['data']['id']:03d}",
            "phonemeCategory": result['data']['category'],
            "sentence": result['data']['sentence'],
            "createdAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Exercise sentence berhasil ditambahkan",
            status_code=status.HTTP_201_CREATED
        )
        
    except HTTPException as e:
        if "not found" in str(e.detail).lower():
            return APIResponse.error(
                message="Kategori phoneme tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        elif "already exists" in str(e.detail):
            return APIResponse.error(
                message="Kalimat sudah ada dalam kategori ini",
                status_code=status.HTTP_409_CONFLICT
            )
        elif "minimal pair" in str(e.detail):
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        elif "must be one of" in str(e.detail):
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.get("/exercise-phoneme/import-template")
def get_exercise_phoneme_template():
    """Get import template for exercise phoneme - RETURNS EXCEL FILE"""
    try:
        template_data = TemplateGenerator.get_template_by_type(MaterialType.SENTENCE)
        buffer = TemplateGenerator.create_excel_buffer(template_data)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=\"exercise_phoneme_template.xlsx\""}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

@pronunciationmaterialrouter.post("/exercise-phoneme/import")
def import_exercise_phoneme(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import Exercise Phoneme Modal - ENHANCED VERSION"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.import_phoneme_sentence_from_excel(file)
        
        response_data = {
            "totalProcessed": result['total_processed'],
            "successCount": result['success_count'],
            "errorCount": result['error_count'],
            "errors": [
                {
                    "row": error["row"],
                    "error": error["reason"]
                } for error in result.get('skipped', [])
            ]
        }
        
        if result['success_count'] > 0:
            message = f"Import berhasil: {result['success_count']} exercise sentence ditambahkan"
            if result['error_count'] > 0:
                message += f", {result['error_count']} error"
        else:
            message = f"Import gagal: {result['error_count']} error ditemukan"
        
        return APIResponse.success(
            data=response_data,
            message=message
        )
        
    except HTTPException as e:
        return APIResponse.error(
            message=str(e.detail),
            status_code=e.status_code
        )
    except Exception as e:
        return APIResponse.error(
            message="Terjadi kesalahan saat import file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.get("/exercise-phoneme/{phoneme_category:path}/detail")
def get_exercise_phoneme_detail(
    phoneme_category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """View Detail Exercise Phoneme (Sentences by Category)"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_phoneme_sentences_by_category(phoneme_category, page, limit)
        
        return APIResponse.success(
            data=result,
            message="Detail exercise sentences berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.put("/exercise-phoneme/sentences/{sentence_id}")
def update_exercise_sentence(
    sentence_id: int,
    request: UpdateSentenceRequest,
    db: Session = Depends(get_db)
):
    """Edit Exercise Sentence"""
    try:
        controller = PronunciationMaterialController(db)
        
        update_payload = {
            "kalimat": request.sentence,
            "fonem": request.phoneme
        }
        
        result = controller.update_phoneme_sentence(sentence_id, update_payload)
        
        response_data = {
            "sentenceId": f"SEN{sentence_id:03d}",
            "sentence": request.sentence,
            "updatedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Exercise sentence berhasil diperbarui"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Sentence tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        elif "must be one of" in str(e.detail):
            return APIResponse.error(
                message=str(e.detail),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.delete("/exercise-phoneme/sentences/{sentence_id}")
def delete_exercise_sentence(
    sentence_id: int,
    db: Session = Depends(get_db)
):
    """Delete exercise sentence"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.delete_phoneme_sentence(sentence_id)
        
        response_data = {
            "sentenceId": f"SEN{sentence_id:03d}",
            "deletedAt": TimestampHelper.get_current_timestamp()
        }
        
        return APIResponse.success(
            data=response_data,
            message="Exercise sentence berhasil dihapus"
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            return APIResponse.error(
                message="Sentence tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        raise e
    except Exception:
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# EXAM PHONEME ENDPOINTS
# ================================

@pronunciationmaterialrouter.get("/exam-phoneme")
def get_exam_phoneme_list(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Exam Phoneme Management List"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_exam_phoneme(search, page, limit)
        
        exam_phonemes = []
        for exam in result["data"]:
            exam_phonemes.append({
                "phonemeCategory": exam["phoneme_category"],
                "totalExam": exam["totalExam"],
                "lastUpdate": exam["last_update"]
            })
            
        return APIResponse.success(
            data={
                "examPhonemes": exam_phonemes,
                "pagination": result.get("pagination", {})
            },
            message="Data exam phoneme berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@pronunciationmaterialrouter.get("/exam-phoneme/{phoneme_category:path}/detail")
def get_exam_phoneme_detail(
    phoneme_category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Phoneme Exam Detail (List of tests by category)"""
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_exam_detail_by_category(phoneme_category, page, limit)
        
        return APIResponse.success(
            data=result,
            message="Detail exam phoneme berhasil diambil."
        )
    except HTTPException as e:
        return APIResponse.error(message=str(e.detail), status_code=e.status_code)
    except Exception as e:
        return APIResponse.error(
            message=f"Terjadi kesalahan server: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )