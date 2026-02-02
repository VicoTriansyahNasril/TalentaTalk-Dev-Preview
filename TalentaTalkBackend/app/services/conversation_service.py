from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.material_repository import MaterialRepository
from app.repositories.score_repository import ScoreRepository
from app.services.llm_service import LLMService
from app.core.exceptions import AppError
import json
import re

class ConversationService:
    def __init__(self, db: AsyncSession):
        self.material_repo = MaterialRepository(db)
        self.score_repo = ScoreRepository(db)

    async def start_session(self):
        topic_obj = await self.material_repo.get_random_topic()
        topic = topic_obj.topic if topic_obj else "General Technology"
        topic_id = topic_obj.idmateripercakapan if topic_obj else None
        
        prompt = f"Generate a unique conversation starter about: '{topic}'. Return ONLY the question."
        question = await LLMService.generate(prompt)
        
        return {"topic": topic, "topic_id": topic_id, "message": question}

    async def process_chat(self, user_input: str, duration: str, talent_id: int, topic_id: int = 1):
        """Memproses chat, hitung score, dan SIMPAN ke DB"""
        
        # 1. WPM Logic (from helper)
        from app.utils.calculation_utils import CalculationHelper
        wpm = CalculationHelper.calculate_wpm(user_input, duration)
        confidence = min(100, max(0, int(wpm)))
        
        # 2. AI Processing
        prompt = f"""
        User said: "{user_input}"
        Task: Check grammar & Respond.
        Return JSON: {{ "grammar_check": "...", "response": "..." }}
        """
        ai_raw = await LLMService.generate(prompt)
        
        # Parse AI
        response_text = ai_raw
        grammar_text = "Analysis included"
        try:
            match = re.search(r'\{.*\}', ai_raw, re.DOTALL)
            if match:
                js = json.loads(match.group())
                response_text = js.get("response", ai_raw)
                grammar_text = js.get("grammar_check", "")
        except:
            pass

        # 3. SAVE TO DB
        await self.score_repo.save_chat_result(
            talent_id=talent_id,
            topic_id=topic_id,
            wpm=wpm,
            grammar=grammar_text[:255]
        )

        return {
            "response": response_text,
            "confidence_score": confidence,
            "grammar_check": grammar_text
        }