# TalentaTalkBackend/utils/validation_helper.py
"""
Reusable validation functions
"""
import re
from typing import List, Optional
from config.constants import AppConstants, ValidationMessages

class ValidationHelper:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> Optional[str]:
        """Validate password and return error message if invalid"""
        if len(password) < AppConstants.MIN_PASSWORD_LENGTH:
            return ValidationMessages.PASSWORD_TOO_SHORT
        return None
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension"""
        return any(filename.lower().endswith(ext) for ext in AppConstants.ALLOWED_FILE_EXTENSIONS)
    
    @staticmethod
    def validate_pagination_limit(limit: int) -> int:
        """Validate and correct pagination limit"""
        return limit if limit in AppConstants.ALLOWED_PAGE_SIZES else AppConstants.DEFAULT_PAGE_SIZE
    
    @staticmethod
    def validate_sentence_length(sentence: str, min_words: int = AppConstants.MIN_SENTENCE_WORDS) -> bool:
        """Validate sentence has minimum number of words"""
        return len(sentence.split()) >= min_words