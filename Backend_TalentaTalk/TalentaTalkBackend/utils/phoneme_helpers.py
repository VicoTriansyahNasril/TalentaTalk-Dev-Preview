# TalentaTalkBackend/utils/phoneme_helpers.py
"""
Additional helper functions specifically for phoneme structure
This file adds new functionality without modifying existing helpers
"""
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from config.phoneme_constants import PhonemeConstants

# ================================
# PHONEME VALIDATION HELPERS
# ================================
class PhonemeValidationHelper:
    """Helper functions for phoneme validation"""
    
    @staticmethod
    def validate_single_phoneme(phoneme: str) -> bool:
        """Validate single phoneme"""
        return PhonemeConstants.is_valid_phoneme(phoneme)
    
    @staticmethod
    def validate_minimal_pair_category(category: str) -> bool:
        """Validate minimal pair category"""
        return PhonemeConstants.validate_minimal_pair_category(category)
    
    @staticmethod
    def validate_phoneme_for_category(phoneme: str, category: str, material_type: str) -> bool:
        """Validate if phoneme is valid for given category"""
        if material_type == "word":
            return phoneme == category
        elif material_type in ["sentence", "exam"]:
            if "-" not in category:
                return False
            phoneme1, phoneme2 = PhonemeConstants.parse_minimal_pair_category(category)
            return phoneme in [phoneme1, phoneme2]
        else:
            return False
    
    @staticmethod
    def get_validation_error_message(phoneme: str, category: str, material_type: str) -> str:
        """Get appropriate validation error message"""
        if not PhonemeConstants.is_valid_phoneme(phoneme):
            return f"Invalid phoneme: {phoneme}"
        
        if material_type == "word" and phoneme != category:
            return f"For word materials, phoneme must match category. Expected: {category}, got: {phoneme}"
        
        if material_type in ["sentence", "exam"]:
            if "-" not in category:
                return f"For {material_type} materials, category must be a minimal pair (e.g., 'i-ɪ', 'p-b')"
            
            phoneme1, phoneme2 = PhonemeConstants.parse_minimal_pair_category(category)
            if phoneme not in [phoneme1, phoneme2]:
                return f"Phoneme '{phoneme}' must be one of [{phoneme1}, {phoneme2}] for category '{category}'"
        
        return "Validation passed"

# ================================
# BUSINESS LOGIC HELPERS
# ================================
class PhonemeBusinessHelper:
    """Business logic helpers for phoneme materials"""
    
    @staticmethod
    def format_phoneme_response_data(materials: List[Any], data_type: str = "words") -> List[Dict[str, Any]]:
        """Format phoneme materials for API response"""
        result = []
        for material in materials:
            formatted_item = {
                "phoneme": material.kategori,
                "lastUpdate": material.updated_at.strftime("%d/%m/%Y") if hasattr(material, 'updated_at') and material.updated_at else "20/6/2025"
            }
            
            if data_type == "words":
                formatted_item["totalWords"] = getattr(material, 'word_count', 0)
            elif data_type == "sentences":
                formatted_item["totalSentence"] = getattr(material, 'sentence_count', 0)
            elif data_type == "exams":
                formatted_item["totalExam"] = getattr(material, 'exam_count', 0)
            
            result.append(formatted_item)
        
        return result
    
    @staticmethod
    def create_id_string(prefix: str, numeric_id: int, padding: int = 3) -> str:
        """Create formatted ID string (e.g., MAT001, SEN002, etc.)"""
        return f"{prefix}{numeric_id:0{padding}d}"
    
    @staticmethod
    def parse_id_string(id_string: str, prefix: str) -> int:
        """Parse formatted ID string to get numeric ID"""
        try:
            return int(id_string.replace(prefix, ""))
        except ValueError:
            return int(id_string)
    
    @staticmethod
    def get_phoneme_type(phoneme: str) -> str:
        """Get phoneme type (vowel, diphthong, consonant)"""
        if phoneme in PhonemeConstants.VOWEL_PHONEMES:
            return "vowel"
        elif phoneme in PhonemeConstants.DIPHTHONG_PHONEMES:
            return "diphthong"
        elif phoneme in PhonemeConstants.CONSONANT_PHONEMES:
            return "consonant"
        else:
            return "unknown"
    
    @staticmethod
    def get_category_info(category: str) -> Dict[str, Any]:
        """Get information about a phoneme category"""
        if "-" in category:
            phoneme1, phoneme2 = PhonemeConstants.parse_minimal_pair_category(category)
            return {
                "category": category,
                "type": "minimal_pair",
                "phoneme1": phoneme1,
                "phoneme2": phoneme2,
                "phoneme1Type": PhonemeBusinessHelper.get_phoneme_type(phoneme1),
                "phoneme2Type": PhonemeBusinessHelper.get_phoneme_type(phoneme2)
            }
        else:
            return {
                "category": category,
                "type": "single_phoneme",
                "phoneme": category,
                "phonemeType": PhonemeBusinessHelper.get_phoneme_type(category),
                "similarPhonemes": PhonemeConstants.get_similar_phonemes(category)
            }

# ================================
# FILE HELPERS
# ================================
class PhonemeFileHelper:
    """File handling helpers for phoneme materials"""
    
    @staticmethod
    def validate_upload_file(file) -> Optional[str]:
        """Validate uploaded file and return error message if invalid"""
        if not file.filename:
            return "No file provided"
        
        if not file.filename.lower().endswith(('.xlsx', '.csv')):
            return "Only .xlsx and .csv files are supported"
        
        if file.size == 0:
            return "File cannot be empty"
        
        if file.size > 10 * 1024 * 1024:
            return "File size must not exceed 10MB"
        
        return None

# ================================
# ERROR HANDLING HELPERS
# ================================
class PhonemeErrorHelper:
    """Error handling helpers for phoneme operations"""
    
    @staticmethod
    def handle_phoneme_validation_error(phoneme: str, category: str = None, material_type: str = None) -> HTTPException:
        """Handle phoneme validation errors"""
        if not PhonemeConstants.is_valid_phoneme(phoneme):
            return HTTPException(
                status_code=400,
                detail=f"Invalid phoneme: {phoneme}. Must be one of: {', '.join(PhonemeConstants.get_all_phonemes()[:10])}..."
            )
        
        if material_type == "word" and category and phoneme != category:
            return HTTPException(
                status_code=400,
                detail=f"For word materials, phoneme must match category. Expected: {category}, got: {phoneme}"
            )
        
        if material_type == "exam" and category and "-" not in category:
            return HTTPException(
                status_code=400,
                detail="Exam materials must use minimal pair categories (e.g., 'i-ɪ', 'p-b')"
            )
        
        return HTTPException(status_code=400, detail="Phoneme validation failed")
    
    @staticmethod
    def handle_minimal_pair_validation_error(category: str) -> HTTPException:
        """Handle minimal pair validation errors"""
        if "-" not in category:
            return HTTPException(
                status_code=400,
                detail=f"Category '{category}' is not a minimal pair. Use format like 'i-ɪ', 'p-b', 's-z'"
            )
        
        if not PhonemeConstants.validate_minimal_pair_category(category):
            return HTTPException(
                status_code=400,
                detail=f"Invalid minimal pair: {category}. Phonemes must be similar enough for contrastive practice"
            )
        
        return HTTPException(status_code=400, detail="Minimal pair validation failed")
    
    @staticmethod
    def handle_database_error(error: Exception) -> HTTPException:
        """Handle database errors consistently"""
        error_msg = str(error)
        
        if "duplicate key value" in error_msg.lower():
            return HTTPException(status_code=409, detail="Data already exists")
        elif "foreign key constraint" in error_msg.lower():
            return HTTPException(status_code=400, detail="Cannot delete: data is referenced by other records")
        else:
            return HTTPException(status_code=500, detail="Database error occurred")
    
    @staticmethod
    def handle_not_found(resource: str = "Data") -> HTTPException:
        """Handle not found errors"""
        return HTTPException(status_code=404, detail=f"{resource} not found")

# ================================
# RESPONSE HELPERS
# ================================
class PhonemeResponseHelper:
    """Response formatting helpers for phoneme operations"""
    
    @staticmethod
    def format_material_response(material_data: dict, prefix: str) -> dict:
        """Format material response data with consistent structure"""
        from utils.timestamp_helper import TimestampHelper
        
        return {
            f"{prefix.lower()}Id": PhonemeBusinessHelper.create_id_string(prefix, material_data["id"]),
            **{k: v for k, v in material_data.items() if k != "id"},
            "createdAt": TimestampHelper.get_current_timestamp()
        }
    
    @staticmethod
    def format_import_response(success_count: int, error_count: int, errors: List[Dict]) -> Dict[str, Any]:
        """Format import response consistently"""
        return {
            "totalProcessed": success_count + error_count,
            "successCount": success_count,
            "errorCount": error_count,
            "errors": [
                {"row": error.get("row", "unknown"), "error": error.get("reason", str(error))}
                for error in errors
            ]
        }
    
    @staticmethod
    def format_exam_response(exam_data: dict, sentences: List[Dict]) -> Dict[str, Any]:
        """Format exam response with sentences"""
        from utils.timestamp_helper import TimestampHelper
        
        sentences_data = []
        for i, sentence in enumerate(sentences, 1):
            sentences_data.append({
                "sentenceId": PhonemeBusinessHelper.create_id_string("SEN", 100 + i),
                "sentence": sentence["sentence"],
                "phoneme": sentence["phoneme"],
                "sentenceOrder": i
            })
        
        return {
            "examId": PhonemeBusinessHelper.create_id_string("EXM", exam_data["exam_id"]),
            "phonemeCategory": exam_data["category"],
            "totalSentencesAdded": len(sentences),
            "sentences": sentences_data,
            "categoryInfo": PhonemeBusinessHelper.get_category_info(exam_data["category"]),
            "createdAt": TimestampHelper.get_current_timestamp()
        }