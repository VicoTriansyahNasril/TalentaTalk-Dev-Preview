# view/InterviewMaterialView.py
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional, List

from utils.timestamp_helper import TimestampHelper
from controller.AuthController import get_current_admin_user
from controller.PronunciationMaterialController import PronunciationMaterialController
from database import get_db
from utils.response_formatter import APIResponse

interviewrouter = APIRouter(
    prefix="/web/admin", 
    dependencies=[Depends(get_current_admin_user)]
)

class AddQuestionRequest(BaseModel):
    interview_question: str

    @validator('interview_question')
    def validate_question_length(cls, v):
        if len(v.split()) < 5:
            raise ValueError('Interview question must contain at least 5 words')
        return v

class UpdateQuestionRequest(BaseModel):
    interview_question: str

    @validator('interview_question')
    def validate_question_length(cls, v):
        if len(v.split()) < 5:
            raise ValueError('Interview question must contain at least 5 words')
        return v

class SwapOrderRequest(BaseModel):
    direction: str

class ReorderRequest(BaseModel):
    question_ids_order: List[int]

@interviewrouter.get("/interview-questions")
def get_interview_questions(
    search: str = Query(None, description="Search by question"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, description="Page size (10, 25, 50)"),
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_interview_questions(search, page, size)
        return APIResponse.success(
            data=result,
            message="Data interview questions berhasil diambil"
        )
    except Exception as e:
        print(f"Error in get_interview_questions: {str(e)}")
        return APIResponse.error(
            message="Terjadi kesalahan server",
            status_code=500
        )

@interviewrouter.post("/interview-questions")
def add_interview_question(
    request: AddQuestionRequest,
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.add_interview_material(request.interview_question)
        response_data = {
            "questionId": f"QST{result['data']['id']:03d}",
            "interviewQuestion": result['data']['interview_question'],
            "createdAt": TimestampHelper.get_current_timestamp()
        }
        return APIResponse.success(
            data=response_data,
            message="Interview question berhasil ditambahkan",
            status_code=201
        )
    except Exception as e:
        if "already exists" in str(e):
            return APIResponse.error(message="Question sudah ada", status_code=409)
        if "validation" in str(e).lower() or "must contain at least" in str(e):
            return APIResponse.error(message=str(e), status_code=400)
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

# PERBAIKAN: Pindahkan endpoint mobile-order SEBELUM endpoint dengan path parameter
@interviewrouter.get("/interview-questions/mobile-order")
def get_questions_for_mobile(
    limit: Optional[int] = Query(None, description="Limit number of questions"),
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_questions_for_mobile(limit)
        return APIResponse.success(
            data=result,
            message="Questions for mobile retrieved successfully"
        )
    except Exception as e:
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

@interviewrouter.post("/interview-questions/reorder")
def reorder_questions(
    request: ReorderRequest,
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.reorder_all_questions(request.question_ids_order)
        return APIResponse.success(data=result["data"], message=result["message"])
    except Exception as e:
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

@interviewrouter.put("/interview-questions/{question_id}")
def update_interview_question(
    question_id: int = Path(..., description="ID of the question to update"),
    request: UpdateQuestionRequest = ...,
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.update_interview_question(question_id, request.interview_question)
        response_data = {
            "questionId": f"QST{question_id:03d}",
            "interviewQuestion": request.interview_question,
            "updatedAt": TimestampHelper.get_current_timestamp()
        }
        return APIResponse.success(
            data=response_data,
            message="Interview question berhasil diperbarui"
        )
    except Exception as e:
        if "not found" in str(e).lower():
            return APIResponse.error(message="Interview question tidak ditemukan", status_code=404)
        if "validation" in str(e).lower() or "must contain at least" in str(e):
            return APIResponse.error(message=str(e), status_code=400)
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

@interviewrouter.delete("/interview-questions/{question_id}")
def delete_interview_question(
    question_id: int = Path(..., description="ID of the question to delete"),
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.delete_interview_question(question_id)
        response_data = {
            "questionId": f"QST{question_id:03d}",
            "deletedAt": TimestampHelper.get_current_timestamp() 
        }
        return APIResponse.success(
            data=response_data,
            message="Interview question berhasil dihapus"
        )
    except Exception as e:
        if "not found" in str(e).lower():
            return APIResponse.error(message="Interview question tidak ditemukan", status_code=404)
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

@interviewrouter.get("/interview-questions/{question_id}")
def get_interview_question_by_id(
    question_id: int = Path(..., description="ID of the question"),
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.get_interview_question_by_id(question_id)
        response_data = {
            "questionId": f"QST{result['id']:03d}",
            "interviewQuestion": result['interview_question'],
            "createdAt": TimestampHelper.format_timestamp(result['updated_at']) if result['updated_at'] else TimestampHelper.get_current_timestamp()
        }
        return APIResponse.success(
            data=response_data,
            message="Interview question berhasil diambil"
        )
    except Exception as e:
        if "not found" in str(e).lower():
            return APIResponse.error(message="Interview question tidak ditemukan", status_code=404)
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

@interviewrouter.post("/interview-questions/{question_id}/swap")
def swap_question_order(
    question_id: int = Path(..., description="ID of the question to swap"),
    request: SwapOrderRequest = ...,
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.swap_question_order(question_id, request.direction)
        return APIResponse.success(data=result["data"], message=result["message"])
    except Exception as e:
        if "not found" in str(e).lower():
            return APIResponse.error(message="Interview question tidak ditemukan", status_code=404)
        if "already at the top" in str(e) or "already at the bottom" in str(e):
            return APIResponse.error(message=str(e), status_code=400)
        return APIResponse.error(message="Terjadi kesalahan server", status_code=500)

@interviewrouter.post("/interview-questions/{question_id}/toggle")
def toggle_interview_question_status(
    question_id: int,
    db: Session = Depends(get_db)
):
    try:
        controller = PronunciationMaterialController(db)
        result = controller.toggle_interview_question_status(question_id)
        return APIResponse.success(data=result["data"], message=result["message"])
    except HTTPException as e:
        return APIResponse.error(message=str(e.detail), status_code=e.status_code)
    except Exception as e:
        return APIResponse.error(message=f"Terjadi kesalahan server: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)