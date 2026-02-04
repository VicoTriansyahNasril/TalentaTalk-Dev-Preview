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

    # Hardcoded Topics
    HARDCODED_TOPICS = [
        {"id": 1, "title": "Technology Trends", "description": "Discussing AI, Blockchain, and future tech."},
        {"id": 2, "title": "Job Interview", "description": "General job interview preparation."},
        {"id": 3, "title": "Daily Routine", "description": "Talk about hobbies, work, and daily life."},
        {"id": 4, "title": "Travel & Culture", "description": "Discussing vacation spots and cultural differences."},
        {"id": 5, "title": "Business Meeting", "description": "Simulate a formal business meeting environment."},
    ]

    async def get_topics(self):
        return self.HARDCODED_TOPICS

    async def start_session(self):
        return {"topic": "Select a topic", "message": "Please select a topic to begin."}

    async def process_chat(self, user_input: str, duration: str, talent_id: int, topic_id: int = 1):
        selected_topic = next((t for t in self.HARDCODED_TOPICS if t["id"] == topic_id), self.HARDCODED_TOPICS[0])
        topic_name = selected_topic["title"]

        from app.utils.calculation_utils import CalculationHelper
        wpm = CalculationHelper.calculate_wpm(user_input, duration)
        confidence = min(100, max(0, int(wpm)))
        
        prompt = f"""
        Context: Professional Conversation about '{topic_name}'.
        User said: "{user_input}"
        Task: Check grammar & Respond naturally relevant to the topic.
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

        await self.score_repo.save_chat_result(
            talent_id=talent_id,
            topic_id=1, 
            wpm=wpm,
            grammar=grammar_text[:255]
        )

        return {
            "response": response_text,
            "confidence_score": confidence,
            "grammar_check": grammar_text
        }