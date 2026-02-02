from datetime import datetime, timedelta
import pytz
from typing import Optional, List

class TimeUtils:
    WIB_TZ = pytz.timezone('Asia/Jakarta')

    @staticmethod
    def get_current_time() -> datetime:
        return datetime.now(pytz.utc)

    @staticmethod
    def format_to_wib(dt: Optional[datetime]) -> str:
        if not dt: return "N/A"
        if dt.tzinfo is None: dt = pytz.utc.localize(dt)
        return dt.astimezone(TimeUtils.WIB_TZ).strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def calculate_streaks(dates: List[datetime]) -> tuple[int, int]:
        """
        Menghitung Streak dengan presisi tinggi.
        Hanya menghitung tanggal unik (1 aktivitas per hari cukup untuk streak).
        """
        if not dates:
            return 0, 0
            
        # 1. Konversi ke Date Only di Timezone WIB dan Unikkan
        unique_dates = set()
        for d in dates:
            if d.tzinfo is None: d = pytz.utc.localize(d)
            unique_dates.add(d.astimezone(TimeUtils.WIB_TZ).date())
            
        sorted_dates = sorted(list(unique_dates), reverse=True)
        
        # 2. Hitung Current Streak
        today = datetime.now(TimeUtils.WIB_TZ).date()
        yesterday = today - timedelta(days=1)
        
        current_streak = 0
        
        # Cek apakah streak dimulai hari ini atau kemarin
        if sorted_dates and (sorted_dates[0] == today or sorted_dates[0] == yesterday):
            current_streak = 1
            for i in range(1, len(sorted_dates)):
                # Jika selisih hari = 1, streak berlanjut
                if (sorted_dates[i-1] - sorted_dates[i]).days == 1:
                    current_streak += 1
                else:
                    break
        
        # 3. Hitung Highest Streak
        highest_streak = 0
        if sorted_dates:
            temp_streak = 1
            for i in range(1, len(sorted_dates)):
                if (sorted_dates[i-1] - sorted_dates[i]).days == 1:
                    temp_streak += 1
                else:
                    highest_streak = max(highest_streak, temp_streak)
                    temp_streak = 1
            highest_streak = max(highest_streak, temp_streak)
            
        return highest_streak, current_streak