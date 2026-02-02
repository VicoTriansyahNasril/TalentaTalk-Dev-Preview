from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.base import BaseRepository
from app.models.models import Manajemen
from app.utils.time_utils import TimeUtils
from app.core.exceptions import NotFoundError
from passlib.context import CryptContext
from typing import List, Dict, Optional
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.repo = DashboardRepository(db)
        self.db = db

    async def get_admin_dashboard(
        self, 
        limit: int = 10, 
        days_back: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        stats = await self.repo.get_total_counts()
        activities = await self.repo.get_recent_activities(
            limit=limit, 
            days_back=days_back,
            start_date=start_date,
            end_date=end_date
        )
        
        formatted_activities = []
        for act in activities:
            new_act = dict(act)
            new_act["date"] = TimeUtils.format_to_wib(act["date"])
            formatted_activities.append(new_act)

        return {
            "statistics": stats,
            "recentActivities": formatted_activities,
            "filter": {
                "limit": limit,
                "daysBack": days_back,
                "dateRange": "Custom" if start_date else f"Last {days_back} days"
            }
        }

    async def get_leaderboard(self, category: str, page: int, limit: int, search: str):
        data = []
        total_records = 0
        
        if category == "topActive":
            all_talents = await self.repo.get_all_talents(search)
            all_activities = await self.repo.get_all_activities_dates()
            talent_dates: Dict[int, List[datetime]] = {t.idtalent: [] for t in all_talents}
            for row in all_activities:
                if row.idtalent in talent_dates:
                    talent_dates[row.idtalent].append(row.waktulatihan)
            
            processed_talents = []
            for talent in all_talents:
                dates = talent_dates[talent.idtalent]
                highest, current = TimeUtils.calculate_streaks(dates)
                processed_talents.append({
                    "id": talent.idtalent,
                    "talentName": talent.nama,
                    "email": talent.email,
                    "highestStreak": f"{highest} Days",
                    "currentStreak": f"{current} Days",
                    "_sort_current": current,
                    "_sort_highest": highest
                })
            
            processed_talents.sort(key=lambda x: (-x["_sort_current"], -x["_sort_highest"], x["talentName"]))
            total_records = len(processed_talents)
            start_idx = (page - 1) * limit
            paged_data = processed_talents[start_idx:start_idx+limit]
            
            for i, item in enumerate(paged_data):
                clean_item = {k: v for k, v in item.items() if not k.startswith('_')}
                clean_item["no"] = start_idx + i + 1
                data.append(clean_item)

        elif category in ["phoneme_material_exercise", "phoneme_exercise"]:
            type_latihan = "Word" if category == "phoneme_material_exercise" else "Sentence"
            results = await self.repo.get_highest_scoring_phoneme(type_latihan)
            if search: results = [r for r in results if search.lower() in r.nama.lower()]
            total_records = len(results)
            sorted_res = sorted(results, key=lambda x: (-x.avg_score, -x.attempted))
            start_idx = (page - 1) * limit
            paged = sorted_res[start_idx:start_idx+limit]
            for i, row in enumerate(paged):
                data.append({
                    "no": start_idx + i + 1, "id": row.idtalent, "talentName": row.nama, "email": row.email,
                    "overallCompletion": f"{row.attempted} attempted", "overallPercentage": f"{row.avg_score:.0f}%", "completionRate": "N/A"
                })

        elif category == "phoneme_exam":
            results = await self.repo.get_highest_scoring_exam()
            if search: results = [r for r in results if search.lower() in r.nama.lower()]
            total_records = len(results)
            sorted_res = sorted(results, key=lambda x: (-x.avg_score, -x.categories_attempted))
            start_idx = (page - 1) * limit
            paged = sorted_res[start_idx:start_idx+limit]
            for i, row in enumerate(paged):
                data.append({
                    "no": start_idx + i + 1, "id": row.idtalent, "talentName": row.nama, "email": row.email,
                    "overallCompletion": f"{row.categories_attempted} categories", "overallPercentage": f"{row.avg_score:.0f}%", "totalAttempts": row.total_attempts
                })

        elif category in ["conversation", "interview"]:
            is_interview = category == "interview"
            results = await (self.repo.get_highest_scoring_interview() if is_interview else self.repo.get_highest_scoring_conversation())
            if search: results = [r for r in results if search.lower() in r.nama.lower()]
            total_records = len(results)
            sorted_res = sorted(results, key=lambda x: (-x.avg_wpm, -x.total_attempts))
            start_idx = (page - 1) * limit
            paged = sorted_res[start_idx:start_idx+limit]
            for i, row in enumerate(paged):
                data.append({
                    "no": start_idx + i + 1, "id": row.idtalent, "talentName": row.nama, "email": row.email,
                    "wpm": f"{row.avg_wpm:.0f} WPM", "totalAttempts": row.total_attempts, "date": TimeUtils.format_to_wib(row.last_date)
                })

        total_pages = (total_records + limit - 1) // limit if limit > 0 else 0
        showing_start = ((page - 1) * limit) + 1 if total_records > 0 else 0
        showing_end = min(page * limit, total_records)
        
        return {
            "learners": data,
            "pagination": {
                "currentPage": page, "totalPages": total_pages, "totalRecords": total_records,
                "showing": f"Showing {showing_start} to {showing_end} of {total_records} entries"
            }
        }

    async def update_admin(self, admin_id: int, nama: str, email: str):
        repo_base = BaseRepository(Manajemen, self.db)
        admin = await repo_base.get_by_id(admin_id)
        if not admin: raise NotFoundError("Admin")
        existing = await self.repo.get_admin_by_email(email)
        if existing and existing.idmanajemen != admin_id: raise ValueError("Email already used")
        return await repo_base.update(admin, {"namamanajemen": nama, "email": email})

    async def change_admin_password(self, admin_id: int, new_password: str):
        repo_base = BaseRepository(Manajemen, self.db)
        admin = await repo_base.get_by_id(admin_id)
        if not admin: raise NotFoundError("Admin")
        hashed = pwd_context.hash(new_password)
        return await repo_base.update(admin, {"password": hashed})