# InterviewOllamaView.py
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.orm import Session
from schemas import AnswerRequest, InterviewSummaryResponse, SummaryRequest, InterviewResponse
from controller.InterviewOllamaController import (
    start_interview_logic, 
    answer_question_logic, 
    get_interview_summary, 
    save_interview_summary,
    get_session_id,
    conversation_sessions
)
from database import get_db
import logging
from controller.AuthController import get_current_user

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

interviewrouter = APIRouter(prefix="/interview", tags=["Interview"])

@interviewrouter.get("/start")
async def start_interview(request: Request, db: Session = Depends(get_db)):
    """
    Memulai sesi interview baru dan mengembalikan pertanyaan pertama
    """
    try:
        # Get session ID using the controller's function
        session_id = get_session_id(request)
        
        # Call async controller function
        result = await start_interview_logic(db, session_id)
        
        if "error" in result:
            logger.error(f"Error starting interview: {result['error']}")
            raise HTTPException(status_code=404, detail=result["error"])
        
        logger.info(f"Interview started successfully for session: {session_id}")
        return result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in start_interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while starting interview")

@interviewrouter.post("/answer", response_model=InterviewResponse)
async def answer_question(request: Request, request_model: AnswerRequest, db: Session = Depends(get_db)):
    """
    Memproses jawaban dari pengguna dengan durasi dan mengembalikan feedback terpisah dengan pertanyaan/message
    Format input: {"answer": "text", "duration": "MM:SS"}
    
    Note: Grammar analysis will be done at the end during summary generation to reduce API calls.
    """
    try:
        # Get session ID using the controller's function
        session_id = get_session_id(request)
        
        # Validasi input
        if not request_model.answer or not request_model.answer.strip():
            raise HTTPException(status_code=400, detail="Answer cannot be empty")
        
        if not request_model.duration:
            raise HTTPException(status_code=400, detail="Duration is required")
        
        # Convert to dict format for the logic function
        answer_data = {
            "answer": request_model.answer.strip(),
            "duration": request_model.duration
        }
        
        # Call async controller function
        result = await answer_question_logic(answer_data, session_id)
        
        if "error" in result:
            logger.error(f"Error processing answer: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"Answer processed successfully for session: {session_id}")
        return result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in answer_question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while processing answer")

@interviewrouter.post("/summary", response_model=InterviewSummaryResponse)
async def get_summary(request: Request, db: Session = Depends(get_db),  authorization: str = Header(None)):
    """
    Menghasilkan dan menyimpan ringkasan interview dengan format JSON yang mencakup:
    - Strengths dan Weaknesses
    - WPM analysis (calculated at the end)
    - Grammar check results (analyzed at the end in batch)
    - Overall performance assessment
    
    This endpoint performs all WPM calculations and grammar analysis in one go to minimize API calls.
    """
    try:
        current_user = get_current_user(authorization)
        talent_id = current_user["idtalent"]
        print(f"Talent ID: {talent_id}")
        # Get session ID using the controller's function
        session_id = get_session_id(request)
        
        # Validasi talent_id
        if not talent_id or talent_id <= 0:
            raise HTTPException(status_code=400, detail="Valid talent_id is required")
        
        # Get summary dari Gemini (includes batch grammar analysis and WPM calculation)
        summary_result = await get_interview_summary(db, talent_id, session_id)
        
        # Check if the summary retrieval was successful
        if summary_result.get("success"):
            # Save the summary to the database
            save_result = await save_interview_summary(
                db, 
                talent_id, 
                summary_result.get("summary", {}),  # Pass summary data
                summary_result.get("statistics", {})  # Pass statistics separately
            )
            
            logger.info(f"Interview summary generated and saved for talent_id: {talent_id}")
            
            # Return the response with the summary and save result
            return {
                "success": True,
                "summary": summary_result.get("summary"),
                "statistics": summary_result.get("statistics"),
                "message": save_result.get("message", "Summary saved successfully"),
                "id": save_result.get("id")  # Return the ID of the saved summary
            }
        else:
            error_message = summary_result.get("error") or summary_result.get("message", "Unknown error")
            logger.error(f"Failed to generate summary: {error_message}")
            
            return {
                "success": False,
                "error": error_message,
                "message": summary_result.get("message"),
                "summary": None,
                "statistics": None,
                "id": None
            }
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in get_summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while generating summary")

@interviewrouter.get("/status")
async def get_interview_status(request: Request):
    """
    Endpoint untuk mengecek status interview saat ini dengan informasi tambahan
    Uses conversation_sessions instead of request.session
    """
    try:
        # Get session ID using the controller's function
        session_id = get_session_id(request)
        
        # Get session data from conversation_sessions
        session_data = conversation_sessions.get(session_id, {})
        
        # Calculate WPM statistics if available
        all_answers = session_data.get("all_answers", [])
        avg_wpm = 0
        if all_answers:
            total_wpm = sum([ans.get("wpm", 0) for ans in all_answers])
            avg_wpm = round(total_wpm / len(all_answers), 1) if len(all_answers) > 0 else 0
        
        status = {
            "session_id": session_id,
            "interview_started": "current_question_index" in session_data,
            "interview_completed": session_data.get("interview_completed", False),
            "current_question_index": session_data.get("current_question_index", -1),
            "total_questions": len(session_data.get("interview_questions", [])),
            "questions_answered": len(all_answers),
            "current_step": session_data.get("current_step", "not_started"),
            "average_wpm": avg_wpm,
            "session_exists": session_id in conversation_sessions
        }
        
        return {"success": True, "status": status}
        
    except Exception as e:
        logger.error(f"Error getting interview status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while getting status")

@interviewrouter.delete("/reset")
async def reset_interview_session(request: Request):
    """
    Reset current interview session - useful for testing or starting fresh
    """
    try:
        # Get session ID using the controller's function
        session_id = get_session_id(request)
        
        # Remove session from conversation_sessions if it exists
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
            logger.info(f"Interview session reset for session: {session_id}")
            return {"success": True, "message": "Interview session has been reset"}
        else:
            return {"success": True, "message": "No active interview session found"}
        
    except Exception as e:
        logger.error(f"Error resetting interview session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while resetting session")

@interviewrouter.get("/debug/sessions")
async def debug_sessions():
    """
    Debug endpoint to see active conversation sessions
    Only use in development - remove in production
    """
    try:
        session_info = {}
        for session_id, data in conversation_sessions.items():
            session_info[session_id] = {
                "current_question_index": data.get("current_question_index", -1),
                "interview_completed": data.get("interview_completed", False),
                "current_step": data.get("current_step", "unknown"),
                "total_answers": len(data.get("all_answers", [])),
                "total_questions": len(data.get("interview_questions", []))
            }
        
        return {
            "success": True,
            "active_sessions": len(conversation_sessions),
            "sessions": session_info
        }
        
    except Exception as e:
        logger.error(f"Error in debug sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while getting debug info")