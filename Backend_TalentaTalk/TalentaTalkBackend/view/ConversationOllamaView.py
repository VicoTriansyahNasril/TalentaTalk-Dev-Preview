# ConversationOllamaView.py
from fastapi import APIRouter, Depends, Body, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import get_db  # Assuming you have async database dependency
from models import Hasillatihanpercakapan
from controller.ConversationOllamaController import (
    start_chat as start_chat_controller, 
    process_user_input, 
    get_detailed_report, 
    save_report_to_db, 
    clear_session as clear_session_controller 
)
from controller.AuthController import get_current_user
from schemas import ChatInput, StartResponse, ChatResponse, TalentRequest

# Setup logger
logger = logging.getLogger(__name__)

# Create router with /conversation prefix
conversationrouter = APIRouter(prefix="/conversation", tags=["conversation"])

def get_session_id(request: Request) -> str:
    """Extract session ID from request - implement based on your logic"""
    # This is a placeholder - implement based on how you determine session_id
    # Could be from headers, query params, or generated
    return "conversation"  # Default session ID

@conversationrouter.get("/start", response_model=StartResponse)
async def start_conversation(db: AsyncSession = Depends(get_db)):
    """Start a new conversation chat session"""
    try:
        topic = await start_chat_controller(db, session_id="conversation")
        return {"message": "Chat started!", "topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting conversation: {str(e)}")

@conversationrouter.post("/chat", response_model=ChatResponse)
async def send_chat_message(chat_input: ChatInput):
    """Process user chat input"""
    try:
        # Validate input
        if not chat_input.user_input or len(chat_input.user_input.strip()) < 2:
            raise HTTPException(status_code=400, detail="Input too short or meaningless.")
        
        if not chat_input.duration or not chat_input.duration.strip():
            raise HTTPException(status_code=400, detail="Duration is required.")
        
        result = await process_user_input(
            chat_input.user_input.strip(), 
            chat_input.duration.strip(), 
            session_id="conversation"
        )
        
        # Check if there's an error in the result
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["detail"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@conversationrouter.get("/report")
async def get_conversation_report(
    request: Request,
    authorization: str = Header(None), 
    db: Session = Depends(get_db)  # Keep as Session if your get_db returns sync session
):
    """Get detailed conversation report and save to database"""
    try:
        # Validate authorization header
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header is required")
        
        print("Authorization Header:", authorization)
        current_user = get_current_user(authorization)
        
        if not current_user or "idtalent" not in current_user:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        talent_id = current_user["idtalent"]
        
        # Get session ID
        session_id = get_session_id(request)
        
        # Validate talent_id
        if not talent_id or talent_id <= 0:
            raise HTTPException(status_code=400, detail="Valid talent_id is required")

        # Get detailed report
        report_data = await get_detailed_report(session_id=session_id)
        print("Detailed Report:", report_data)

        # Save to database using sync function
        save_result = save_conversation_report_sync(
            db, 
            talent_id, 
            session_id,
            report_data
        )
        print("Save Status:", save_result)

        # Return response
        if save_result.get("success", True):
            return {
                "success": True,
                "report": report_data.get("report", []),
                "message": save_result.get("message", "Report saved successfully"),
                "talent_id": talent_id,
                "id": save_result.get("id")
            }
        else:
            return {
                "success": False,
                "error": save_result.get("error", "Failed to save report"),
                "message": save_result.get("message"),
                "report": None,
                "talent_id": talent_id,
                "id": None
            }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        import traceback
        print("Exception occurred:", traceback.format_exc())
        logger.error(f"Unexpected error in get_conversation_report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while processing report")

# Synchronous helper function for saving conversation report
# Synchronous helper function for saving conversation report (MODIFIED VERSION)
def save_conversation_report_sync(db: Session, talent_id: int, session_id: str, report_data: dict):
    """
    Save conversation report to database (synchronous version)
    Modified to save only ONE record per training session with averaged WPM
    """
    try:
        # Extract data from report
        report_list = report_data.get("report", [])
        
        if not report_list:
            return {
                "success": False,
                "error": "No report data to save",
                "message": "Report data is empty"
            }
        
        # Calculate average WPM from all entries
        total_wpm = 0.0
        wpm_count = 0
        all_grammar_issues = []
        
        for entry in report_list:
            # Extract WPM value from wpm_confidence_info
            wpm_info = entry.get("wpm_confidence_info", "WPM: 0.00")
            wpm_value = 0.0
            
            try:
                # Parse WPM dari string "WPM: 42.00"
                if "WPM:" in wpm_info:
                    wpm_str = wpm_info.split("WPM:")[1].strip()
                    # Handle case where there might be additional text after WPM value
                    wpm_parts = wpm_str.split()
                    if wpm_parts:
                        wpm_value = float(wpm_parts[0])
                        total_wpm += wpm_value
                        wpm_count += 1
            except (ValueError, IndexError):
                wpm_value = 0.0
            
            # Collect all grammar issues from all entries
            grammar_issues = entry.get("grammar_issues", [])
            if grammar_issues:
                for issue in grammar_issues:
                    if issue.get("message"):
                        all_grammar_issues.append(issue.get("message"))
        
        # Calculate average WPM
        average_wpm = total_wpm / wpm_count if wpm_count > 0 else 0.0
        
        # Combine all grammar issues into one string
        combined_grammar = ""
        if all_grammar_issues:
            # Remove duplicates while preserving order
            unique_grammar_issues = list(dict.fromkeys(all_grammar_issues))
            combined_grammar = "; ".join(unique_grammar_issues)
        
        # Create single record with averaged data
        new_record = Hasillatihanpercakapan(
            idtalent=talent_id,
            idmateripercakapan=1,  # Default material ID, sesuaikan dengan kebutuhan
            wpm=round(average_wpm, 2),  # Round to 2 decimal places
            grammar=combined_grammar[:255] if combined_grammar else "No grammar issues found",  # Limit to 255 chars
            waktulatihan=datetime.now()
        )
        
        db.add(new_record)
        
        # Commit the single record (synchronous)
        db.commit()
        
        # Refresh to get ID (synchronous)
        db.refresh(new_record)
        
        return {
            "success": True,
            "message": f"Successfully saved conversation training result with average WPM: {round(average_wpm, 2)}",
            "id": new_record.idhasilpercakapan,
            "average_wpm": round(average_wpm, 2),
            "total_entries_processed": len(report_list)
        }
        
    except Exception as e:
        # Synchronous rollback
        db.rollback()
        logger.error(f"Error saving conversation report: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to save report: {str(e)}"
        }

# Alternative: Async version if you want to use AsyncSession
# Alternative: Async version if you want to use AsyncSession (MODIFIED VERSION)
async def save_conversation_report_async(db: AsyncSession, talent_id: int, session_id: str, report_data: dict):
    """
    Save conversation report to database (asynchronous version)
    Modified to save only ONE record per training session with averaged WPM
    """
    try:
        # Extract data from report
        report_list = report_data.get("report", [])
        
        if not report_list:
            return {
                "success": False,
                "error": "No report data to save",
                "message": "Report data is empty"
            }
        
        # Calculate average WPM from all entries
        total_wpm = 0.0
        wpm_count = 0
        all_grammar_issues = []
        
        for entry in report_list:
            # Extract WPM value from wpm_confidence_info
            wpm_info = entry.get("wpm_confidence_info", "WPM: 0.00")
            wpm_value = 0.0
            
            try:
                # Parse WPM dari string "WPM: 42.00"
                if "WPM:" in wpm_info:
                    wpm_str = wpm_info.split("WPM:")[1].strip()
                    # Handle case where there might be additional text after WPM value
                    wpm_parts = wpm_str.split()
                    if wpm_parts:
                        wpm_value = float(wpm_parts[0])
                        total_wpm += wpm_value
                        wpm_count += 1
            except (ValueError, IndexError):
                wpm_value = 0.0
            
            # Collect all grammar issues from all entries
            grammar_issues = entry.get("grammar_issues", [])
            if grammar_issues:
                for issue in grammar_issues:
                    if issue.get("message"):
                        all_grammar_issues.append(issue.get("message"))
        
        # Calculate average WPM
        average_wpm = total_wpm / wpm_count if wpm_count > 0 else 0.0
        
        # Combine all grammar issues into one string
        combined_grammar = ""
        if all_grammar_issues:
            # Remove duplicates while preserving order
            unique_grammar_issues = list(dict.fromkeys(all_grammar_issues))
            combined_grammar = "; ".join(unique_grammar_issues)
        
        # Create single record with averaged data
        new_record = Hasillatihanpercakapan(
            idtalent=talent_id,
            idmateripercakapan=1,  # Default material ID, sesuaikan dengan kebutuhan
            wpm=round(average_wpm, 2),  # Round to 2 decimal places
            grammar=combined_grammar[:255] if combined_grammar else "No grammar issues found",  # Limit to 255 chars
            waktulatihan=datetime.now()
        )
        
        db.add(new_record)
        
        # Commit the single record (asynchronous)
        await db.commit()
        
        # Refresh to get ID (asynchronous)
        await db.refresh(new_record)
        
        return {
            "success": True,
            "message": f"Successfully saved conversation training result with average WPM: {round(average_wpm, 2)}",
            "id": new_record.idhasilpercakapan,
            "average_wpm": round(average_wpm, 2),
            "total_entries_processed": len(report_list)
        }

    except Exception as e:
        # Asynchronous rollback
        await db.rollback()
        logger.error(f"Error saving conversation report: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to save report: {str(e)}"
        }

@conversationrouter.delete("/session")
async def clear_conversation_session():
    """Clear the current conversation session"""
    try:
        result = clear_session_controller(session_id="conversation")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

# Optional: Add a health check endpoint
@conversationrouter.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "conversation"}