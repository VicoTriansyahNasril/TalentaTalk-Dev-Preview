from datetime import datetime
from app.repositories.material_repository import MaterialRepository
from app.repositories.score_repository import ScoreRepository
from app.services.audio_service import AudioService
from app.services.llm_service import LLMService
from app.utils.phoneme_utils import PhonemeMatcher
from app.core.exceptions import NotFoundError
from gruut import sentences as gruut_sentences

class PhonemeService:
    def __init__(self, material_repo: MaterialRepository, score_repo: ScoreRepository):
        self.material_repo = material_repo
        self.score_repo = score_repo

    def _generate_phonemes_fallback(self, text: str) -> str:
        """Fallback to generate phonemes if DB is empty"""
        try:
            phonemes = []
            for sentence in gruut_sentences(text, lang="en-us"):
                for word in sentence.words:
                    if word.phonemes:
                        phonemes.extend(word.phonemes)
            return " ".join(phonemes)
        except:
            return ""

    async def process_pronunciation(self, talent_id: int, content_id: int, audio_bytes: bytes, type: str):
        # 1. Ambil Target
        content = await self.material_repo.get_phoneme_content(content_id, type)
        if not content:
            raise NotFoundError(f"Material {type}")
            
        target_text = content.kata if type == "word" else content.kalimat
        target_phonemes = content.fonem
        
        # Robustness: Jika DB kosong, generate on-the-fly
        if not target_phonemes:
            target_phonemes = self._generate_phonemes_fallback(target_text)
        
        # 2. Transkripsi Audio
        try:
            user_phonemes = await AudioService.transcribe(audio_bytes)
        except Exception as e:
            # Fallback jika Audio Service error
            print(f"Audio Service Error: {e}")
            user_phonemes = ""
        
        # 3. Scoring
        alignment = PhonemeMatcher.align_phonemes(target_phonemes, user_phonemes)
        accuracy = PhonemeMatcher.calculate_accuracy(alignment)
        
        # 4. AI Analysis (dengan Try-Except agar tidak memblokir flow utama)
        try:
            ai_analysis = await LLMService.analyze_phoneme_quality(
                target_phonemes, user_phonemes, target_text
            )
        except Exception:
            ai_analysis = {"error": "AI Analysis unavailable"}
        
        # 5. Result Object
        result_full = {
            "similarity_percent": f"{accuracy}%",
            "accuracy_score": accuracy,
            "target_phonemes": target_phonemes,
            "user_phonemes": user_phonemes,
            "phoneme_comparison": alignment,
            "gemini_analysis": ai_analysis
        }

        # 6. Save DB
        db_type = "Word" if type.lower() == "word" else "Sentence"
        await self.score_repo.save_phoneme_result(
            talent_id=talent_id,
            soal_id=content_id,
            type=db_type,
            score=accuracy,
            comparison=result_full
        )
        
        return result_full

    async def get_word_by_id(self, id: int):
        word = await self.material_repo.get_word_by_id(id)
        if not word: raise NotFoundError("Word")
        return {
            "idContent": word.idmaterifonemkata,
            "content": word.kata,
            "meaning": word.meaning,
            "definition": word.definition,
            "phoneme": word.fonem,
            "phoneme_category": word.kategori
        }

    async def get_sentence_by_id(self, id: int):
        sent = await self.material_repo.get_sentence_by_id(id)
        if not sent: raise NotFoundError("Sentence")
        return {
            "idContent": sent.idmaterifonemkalimat,
            "content": sent.kalimat,
            "phoneme": sent.fonem,
            "phoneme_category": sent.kategori
        }

    async def get_random_word(self, phoneme: str):
        word = await self.material_repo.get_random_word_by_phoneme(phoneme)
        if not word: return None
        return {
            "idContent": word.idmaterifonemkata,
            "content": word.kata,
            "phoneme": word.fonem,
            "phoneme_category": word.kategori
        }

    async def get_random_sentence(self, phoneme: str):
        sent = await self.material_repo.get_random_sentence_by_phoneme(phoneme)
        if not sent: return None
        return {
            "idContent": sent.idmaterifonemkalimat,
            "content": sent.kalimat,
            "phoneme": sent.fonem,
            "phoneme_category": sent.kategori
        }