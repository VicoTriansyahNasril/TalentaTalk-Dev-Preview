from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Set
from app.core.config import settings

class PhonemeMatcher:
    SIMILAR_PHONEMES = settings.SIMILAR_PHONEMES
    ALL_PHONEMES = settings.VOWEL_PHONEMES + settings.DIPHTHONG_PHONEMES + settings.CONSONANT_PHONEMES
    
    TIE_BAR_NORMALIZATION = {
        "d͡ʒ": "dʒ", "t͡ʃ": "tʃ", "t͡s": "ts", "d͡z": "dz"
    }

    @classmethod
    def get_similar_phonemes(cls, phoneme: str) -> List[str]:
        """Logic pengambilan fonem mirip yang sama persis dengan controller lama"""
        if phoneme not in cls.ALL_PHONEMES:
            return []

        direct_similars = set(cls.SIMILAR_PHONEMES.get(phoneme, []))
        
        inverse_similars = set()
        for key, values in cls.SIMILAR_PHONEMES.items():
            if phoneme in values:
                inverse_similars.add(key)
                inverse_similars.update(cls.SIMILAR_PHONEMES.get(key, []))

        all_similars = direct_similars.union(inverse_similars)
        all_similars.discard(phoneme)
        
        return sorted(list(all_similars))

    @classmethod
    def is_similar(cls, target: str, user: str) -> bool:
        if target == user:
            return True
        similars = cls.get_similar_phonemes(target)
        return user in similars

    @classmethod
    def get_status_score(cls, target: str, user: str) -> Tuple[str, int]:
        if not target and not user: return "correct", 100
        if not target and user: return "extra", 0
        if target and not user: return "missing", 0
        
        if target == user: return "correct", 100
        if cls.is_similar(target, user): return "similar", 75
        
        return "incorrect", 0

    @classmethod
    def align_phonemes(cls, target_str: str, user_str: str) -> List[Dict]:
        target_list = target_str.split()
        user_list = user_str.split()
        
        matcher = SequenceMatcher(None, target_list, user_list)
        alignment = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    t = target_list[i1+k]
                    u = user_list[j1+k]
                    status, score = cls.get_status_score(t, u)
                    alignment.append({
                        "target": t, "user": u, "status": status, "similarity": score
                    })
            elif tag == 'replace':
                len_target = i2 - i1
                len_user = j2 - j1
                max_len = max(len_target, len_user)
                for k in range(max_len):
                    t = target_list[i1+k] if k < len_target else ""
                    u = user_list[j1+k] if k < len_user else ""
                    status, score = cls.get_status_score(t, u)
                    alignment.append({"target": t, "user": u, "status": status, "similarity": score})
            elif tag == 'delete':
                for k in range(i2 - i1):
                    t = target_list[i1+k]
                    status, score = cls.get_status_score(t, "")
                    alignment.append({"target": t, "user": "", "status": status, "similarity": score})
            elif tag == 'insert':
                for k in range(j2 - j1):
                    u = user_list[j1+k]
                    status, score = cls.get_status_score("", u)
                    alignment.append({"target": "", "user": u, "status": status, "similarity": score})
        
        return alignment

    @staticmethod
    def calculate_accuracy(alignment: List[Dict]) -> float:
        if not alignment: return 0.0
        
        total_score = 0
        valid_items = 0
        
        for item in alignment:
            # Mengikuti logika controller lama:
            status = item.get("status")
            if status == "correct": total_score += 100
            elif status == "similar": total_score += 75
            valid_items += 1
            
        return round(total_score / valid_items, 1) if valid_items > 0 else 0.0