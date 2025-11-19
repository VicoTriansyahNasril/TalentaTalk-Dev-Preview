# config/constants.py
"""
Centralized configuration untuk menghindari hard-coded values
"""
from typing import List

class AppConstants:
    # Pagination settings
    ALLOWED_PAGE_SIZES: List[int] = [10, 25, 50]
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 50
    
    # Password settings
    MIN_PASSWORD_LENGTH: int = 8
    DEFAULT_PASSWORD: str = "default123"
    
    # Date formats
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    DISPLAY_DATE_FORMAT: str = "%d/%m/%Y"
    
    # Default values
    DEFAULT_ROLE: str = "talent"
    DEFAULT_ADMIN_ROLE: str = "Manajemen"
    
    # Exam settings
    SENTENCES_PER_EXAM: int = 10
    MIN_SENTENCE_WORDS: int = 10
    MIN_QUESTION_WORDS: int = 5
    
    # File upload settings
    ALLOWED_FILE_EXTENSIONS: List[str] = ['.xlsx', '.csv']
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB


class ValidationMessages:
    # Common validation messages
    REQUIRED_FIELD = "{field} tidak boleh kosong"
    INVALID_EMAIL = "Format email tidak valid"
    PASSWORD_TOO_SHORT = f"Password minimal {AppConstants.MIN_PASSWORD_LENGTH} karakter"
    INVALID_FILE_FORMAT = "Format file tidak didukung. Gunakan {formats}"
    
    # Specific validation messages
    DUPLICATE_EMAIL = "Email sudah terdaftar"
    DUPLICATE_CATEGORY = "Kategori phoneme sudah ada"
    DUPLICATE_WORD = "Kata sudah ada dalam kategori ini"
    DUPLICATE_SENTENCE = "Kalimat sudah ada dalam kategori ini"
    DUPLICATE_QUESTION = "Question sudah ada"
    
    # Not found messages
    TALENT_NOT_FOUND = "Talent tidak ditemukan"
    CATEGORY_NOT_FOUND = "Kategori phoneme tidak ditemukan"
    WORD_NOT_FOUND = "Kata tidak ditemukan"
    QUESTION_NOT_FOUND = "Interview question tidak ditemukan"