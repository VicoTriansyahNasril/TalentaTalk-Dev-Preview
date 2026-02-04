from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview
from datetime import datetime
import pytz

class ScoreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_phoneme_result(self, talent_id: int, soal_id: int, type: str, score: float, comparison: dict):
        result = Hasillatihanfonem(
            idtalent=talent_id,
            idsoal=soal_id,
            typelatihan=type,
            nilai=score,
            phoneme_comparison=comparison,
            waktulatihan=datetime.now(pytz.utc)
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def save_chat_result(self, talent_id: int, topic_id: int, wpm: float, grammar: str):
        result = Hasillatihanpercakapan(
            idtalent=talent_id,
            idmateripercakapan=topic_id,
            wpm=wpm,
            grammar=grammar,
            waktulatihan=datetime.now(pytz.utc)
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def save_interview_result(self, talent_id: int, wpm: float, grammar: str, feedback: str):
        result = Hasillatihaninterview(
            idtalent=talent_id,
            wpm=wpm,
            grammar=grammar,
            feedback=feedback,
            waktulatihan=datetime.now(pytz.utc)
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result