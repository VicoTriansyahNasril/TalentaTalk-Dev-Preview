class CalculationHelper:
    @staticmethod
    def calculate_wpm(text: str, duration: str) -> float:
        """Kalkulasi Words Per Minute"""
        try:
            words = len(text.split())
            duration = duration.strip()
            
            if ':' in duration:
                time_parts = duration.split(':')
                if len(time_parts) == 2:
                    minutes, seconds = map(int, time_parts)
                    total_seconds = minutes * 60 + seconds
                else:
                    return 0.0
            else:
                total_seconds = int(duration)
            
            if total_seconds <= 0:
                return 0.0
                
            wpm = (words / total_seconds) * 60
            return round(wpm, 2)
        except Exception:
            return 0.0