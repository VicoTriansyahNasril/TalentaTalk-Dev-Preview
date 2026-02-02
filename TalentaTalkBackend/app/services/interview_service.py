from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.material_repository import MaterialRepository
from app.repositories.score_repository import ScoreRepository
from app.services.llm_service import LLMService
from app.utils.calculation_utils import CalculationHelper
from app.core.exceptions import AppError, NotFoundError
import json
import uuid
from typing import Dict, Any

class InterviewService:
    _sessions: Dict[str, Any] = {}

    def __init__(self, db: AsyncSession):
        self.material_repo = MaterialRepository(db)
        self.score_repo = ScoreRepository(db)

    async def start_session(self, session_id: str):
        if not session_id: session_id = str(uuid.uuid4())
        questions = await self.material_repo.get_interview_questions(0, 100)
        if not questions: raise NotFoundError("Interview Questions")
        self._sessions[session_id] = {"questions": [q.question for q in questions], "current_index": 0, "step": "main", "history": [], "answers": [], "completed": False, "off_topic_count": 0}
        return {"session_id": session_id, "question": questions[0].question, "step": "main"}

    async def get_session_status(self, session_id: str):
        session = self._sessions.get(session_id)
        if not session: return {"status": "not_found", "session_exists": False}
        return {"success": True, "status": {"session_id": session_id, "interview_started": True, "interview_completed": session["completed"], "current_question_index": session["current_index"], "total_questions": len(session["questions"]), "current_step": session["step"], "session_exists": True}}

    async def process_answer(self, session_id: str, answer: str, duration: str):
        session = self._sessions.get(session_id)
        if not session: raise AppError(status_code=400, detail="Session expired. Please restart.")
        if session["completed"]: return {"status": "completed", "message": "Interview already finished."}
        current_q_text = session["questions"][session["current_index"]]
        
        if session["step"] == "main":
            relevance = await LLMService.check_relevance(current_q_text, answer)
            if not relevance.get("is_relevant", True):
                session["off_topic_count"] += 1
                return {"status": "off_topic", "message": f"Your answer seems unrelated. {relevance.get('reason', 'Please focus on the question.')} Let's try again: {current_q_text}", "interview_completed": False}

        wpm = CalculationHelper.calculate_wpm(answer, duration)
        session["answers"].append({"question": current_q_text, "answer": answer, "wpm": wpm})
        session["history"].append({"role": "user", "content": answer})

        if session["step"] == "main":
            ai_resp = await LLMService.generate_interview_followup(current_q_text, answer)
            session["step"] = "followup"
            followup_q = ai_resp.get("followup_question", "Could you explain more?")
            session["history"].append({"role": "interviewer", "content": followup_q})
            return {"status": "continue", "feedback": ai_resp.get("feedback", "Good."), "message": followup_q, "interview_completed": False}
            
        elif session["step"] == "followup":
            session["current_index"] += 1
            session["step"] = "main"
            if session["current_index"] >= len(session["questions"]):
                session["completed"] = True
                return {"status": "completed", "feedback": "Excellent. That concludes our interview.", "message": "Interview completed.", "interview_completed": True}
            next_q = session["questions"][session["current_index"]]
            session["history"].append({"role": "interviewer", "content": next_q})
            return {"status": "continue", "feedback": "Thank you.", "message": next_q, "interview_completed": False}

    async def generate_summary(self, session_id: str, talent_id: int):
        session = self._sessions.get(session_id)
        if not session: raise AppError(status_code=400, detail="Session not found")
        ai_summary = await LLMService.generate_interview_feedback(session["history"])
        answers = session["answers"]
        total_wpm = sum(a["wpm"] for a in answers)
        avg_wpm = total_wpm / len(answers) if answers else 0
        grammar_score = ai_summary.get("summary", {}).get("overall_performance", {}).get("grammar_usage", "Fair")
        saved_record = await self.score_repo.save_interview_result(talent_id=talent_id, wpm=avg_wpm, grammar=grammar_score, feedback=json.dumps(ai_summary))
        if session_id in self._sessions: del self._sessions[session_id]
        return {"success": True, "summary": ai_summary.get("summary"), "statistics": {"average_wpm": round(avg_wpm, 2), "total_answers": len(answers)}, "id": saved_record.idhasilinterview}