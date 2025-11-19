# TalentaTalkBackend/utils/date_helper.py
"""
Helper untuk date handling yang konsisten
"""
from datetime import datetime
from config.constants import AppConstants

class DateHelper:
    @staticmethod
    def format_date(date_obj: datetime) -> str:
        """Format date untuk display"""
        if not date_obj:
            return ""
        return date_obj.strftime(AppConstants.DISPLAY_DATE_FORMAT)
    
    @staticmethod
    def format_datetime(datetime_obj: datetime) -> str:
        """Format datetime untuk display"""
        if not datetime_obj:
            return ""
        return datetime_obj.strftime(AppConstants.DATETIME_FORMAT)
    
    @staticmethod
    def get_current_datetime_str() -> str:
        """Get current datetime as formatted string"""
        return datetime.now().strftime(AppConstants.DATETIME_FORMAT)