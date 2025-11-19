# view/TalentListView.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from controller.AuthController import get_current_admin_user
from controller.TalentController import TalentController
from database import get_db
from schemas import ChangePasswordRequest, CreateTalentRequest, UpdateTalentRequest
from utils.response_formatter import APIResponse
from utils.template_generator import TemplateGenerator
from config.phoneme_constants import MaterialType

talentlistrouter = APIRouter(
    prefix="/web/admin/talents",
    dependencies=[Depends(get_current_admin_user)]
)

@talentlistrouter.get("")
def get_talent_list(
    searchQuery: Optional[str] = Query(None, alias="searchQuery"),
    page: int = Query(1, ge=1),
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    try:
        controller = TalentController(db)
        result = controller.get_talent_list(search=searchQuery, page=page, size=limit)
        return APIResponse.success(data=result, message="Data talent berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Gagal mengambil data talent: {e}")

@talentlistrouter.get("/import-template")
def get_talent_import_template(db: Session = Depends(get_db)):
    """Endpoint untuk mengunduh template impor talenta dalam format Excel."""
    try:
        template_data = TemplateGenerator.get_template_by_type(MaterialType.TALENT)
        buffer = TemplateGenerator.create_excel_buffer(template_data)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=\"talent_import_template.xlsx\""}
        )
    except Exception as e:
        print(f"Template generation error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Gagal membuat template: {str(e)}"
        )


@talentlistrouter.post("/import")
def import_talents(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Endpoint untuk mengimpor talenta dari file Excel dengan enhanced error handling."""
    try:
        print(f"Import request received for file: {file.filename}")
        print(f"File content type: {file.content_type}")
        
        if not file:
            return APIResponse.error(
                message="Tidak ada file yang dikirim", 
                status_code=400
            )
            
        if not file.filename:
            return APIResponse.error(
                message="Nama file tidak valid", 
                status_code=400
            )
        
        if hasattr(file, 'size') and file.size == 0:
            return APIResponse.error(
                message="File kosong", 
                status_code=400
            )
        
        controller = TalentController(db)
        result = controller.import_talents_from_excel(file)
        
        message = f"Impor selesai: {result['successCount']} berhasil ditambahkan"
        if result['errorCount'] > 0:
            message += f", {result['errorCount']} gagal"
            
        print(f"Import completed: {message}")
        
        return APIResponse.success(data=result, message=message)
        
    except HTTPException as e:
        print(f"HTTPException in import: {e.detail}")
        return APIResponse.error(message=e.detail, status_code=e.status_code)
        
    except ValueError as ve:
        print(f"ValueError in import: {str(ve)}")
        return APIResponse.error(
            message=f"Data tidak valid: {str(ve)}", 
            status_code=400
        )
        
    except FileNotFoundError:
        print("FileNotFoundError in import")
        return APIResponse.error(
            message="File tidak ditemukan atau tidak dapat diakses", 
            status_code=400
        )
        
    except PermissionError:
        print("PermissionError in import")
        return APIResponse.error(
            message="Tidak memiliki izin untuk membaca file", 
            status_code=400
        )
        
    except Exception as e:
        print(f"Unexpected error in import: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return APIResponse.server_error(f"Gagal mengimpor talenta: {str(e)}")
    
@talentlistrouter.get("/{talent_id}")
def get_talent_by_id(talent_id: int, db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_talent_by_id(talent_id)
        return APIResponse.success(data=result, message="Data talent berhasil diambil")
    except HTTPException as e:
        raise e
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.post("")
def add_talent(request: CreateTalentRequest, db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.add_talent(request.nama, request.email, request.role, request.password)
        return APIResponse.success(data=result['data'], message="Talent berhasil ditambahkan", status_code=status.HTTP_201_CREATED)
    except HTTPException as e:
        raise e
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.put("/{talent_id}")
def edit_talent(talent_id: int, request: UpdateTalentRequest, db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.update_talent(talent_id, request.nama, request.email, request.role)
        return APIResponse.success(data=result['data'], message="Data talent berhasil diperbarui")
    except HTTPException as e:
        raise e
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.put("/{talent_id}/change-password")
def change_password(talent_id: int, request: ChangePasswordRequest, db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        controller.change_talent_password(talent_id, request.new_password)
        return APIResponse.success(message="Password talent berhasil diubah")
    except HTTPException as e:
        raise e
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.delete("/{talent_id}")
def delete_talent(talent_id: int, db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        controller.delete_talent(talent_id)
        return APIResponse.success(message="Talent berhasil dihapus")
    except HTTPException as e:
        raise e
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/phoneme-material-exercise")
def get_phoneme_material_exercise(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_material_exercise_progress(talent_id, page, limit)
        return APIResponse.success(data=result, message="Data phoneme material exercise berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/phoneme-material-exercise/{phoneme_category:path}/detail")
def get_phoneme_material_detail(talent_id: int, phoneme_category: str, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_word_detail(talent_id, phoneme_category, page, limit)
        return APIResponse.success(data=result, message="Detail phoneme material exercise berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/phoneme-exercise")
def get_phoneme_exercise_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_exercise_progress(talent_id, page, limit)
        return APIResponse.success(data=result, message="Data phoneme exercise berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/phoneme-exercise/{phoneme_category:path}/detail")
def get_phoneme_exercise_detail(talent_id: int, phoneme_category: str, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_exercise_detail(talent_id, phoneme_category, page, limit)
        return APIResponse.success(data=result, message="Detail phoneme exercise berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")
    
@talentlistrouter.get("/{talent_id}/phoneme-exam")
def get_phoneme_exam_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_exam_progress(talent_id, page, limit)
        return APIResponse.success(data=result, message="Data phoneme exam berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

# PERBAIKAN: Pindahkan endpoint yang lebih spesifik ke atas
@talentlistrouter.get("/{talent_id}/phoneme-exam/attempt/{attempt_id}/detail")
def get_phoneme_exam_attempt_detail(
    talent_id: int, 
    attempt_id: int, 
    db: Session = Depends(get_db)
):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_exam_attempt_detail(talent_id, attempt_id)
        return APIResponse.success(data=result, message="Detail exam attempt berhasil diambil")
    except HTTPException as e:
        raise e
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/phoneme-exam/{phoneme_category:path}/detail")
def get_phoneme_exam_detail(talent_id: int, phoneme_category: str, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_phoneme_exam_detail(talent_id, phoneme_category, page, limit)
        return APIResponse.success(data=result, message="Detail phoneme exam berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/conversation")
def get_conversation_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_conversation_progress(talent_id, page, limit)
        return APIResponse.success(data=result, message="Data conversation berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/interview")
def get_interview_progress(talent_id: int, page: int = Query(1, ge=1), limit: int = Query(10), db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_interview_progress(talent_id, page, limit)
        return APIResponse.success(data=result, message="Data interview berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")

@talentlistrouter.get("/{talent_id}/interview/{attempt_id}/detail")
def get_interview_attempt_detail(talent_id: int, attempt_id: int, db: Session = Depends(get_db)):
    try:
        controller = TalentController(db)
        result = controller.get_interview_attempt_detail(talent_id, attempt_id)
        return APIResponse.success(data=result, message="Detail interview attempt berhasil diambil")
    except Exception as e:
        return APIResponse.server_error(f"Terjadi kesalahan: {e}")