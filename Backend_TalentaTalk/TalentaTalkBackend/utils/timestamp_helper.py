# TalentaTalkBackend/utils/timestamp_helper.py
from datetime import datetime
from typing import Optional
import pytz

class TimestampHelper:
    
    WIB_TZ = pytz.timezone('Asia/Jakarta')

    @staticmethod
    def get_current_utc_time() -> datetime:
        return datetime.utcnow()

    @staticmethod
    def get_current_timestamp() -> str:
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        wib_now = utc_now.astimezone(TimestampHelper.WIB_TZ)
        return wib_now.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_utc_to_wib_str(utc_dt: Optional[datetime]) -> Optional[str]:
        if not utc_dt:
            return None

        utc_dt_aware = pytz.utc.localize(utc_dt)
        
        # Convert to WIB timezone
        wib_dt = utc_dt_aware.astimezone(TimestampHelper.WIB_TZ)
        
        return wib_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_timestamp(dt: Optional[datetime]) -> Optional[str]:
        return TimestampHelper.format_utc_to_wib_str(dt)