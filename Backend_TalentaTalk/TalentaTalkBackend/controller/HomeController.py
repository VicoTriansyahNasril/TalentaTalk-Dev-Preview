# controller/HomeController.py
from typing import Optional, Dict, List, Any, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, case, union_all, text
from datetime import datetime, timedelta
from passlib.context import CryptContext
from utils.pagination import PaginationHelper, paginate_learners_list
from utils.timestamp_helper import TimestampHelper

from models import (
    Talent, Materifonemkata, Materifonemkalimat, Materiinterview,
    Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview,
    Ujianfonem, Manajemen, Materiujian
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HomeController:
    def __init__(self, db: Session):
        self.db = db

    def format_wpm(self, wpm_value: Optional[float]) -> str:
        if wpm_value is None or wpm_value == 0:
            return "0 WPM"
        return f"{wpm_value:.0f} WPM"

    def validate_activity_limit(self, limit: int) -> int:
        if limit is None:
            return 10
        if limit < 1:
            return 1
        elif limit > 200:
            return 200
        return limit

    def get_dashboard_stats(self) -> Dict[str, Any]:
        total_talent = self.db.query(func.count(Talent.idtalent)).scalar() or 0
        total_pronunciation_material = (self.db.query(func.count(Materifonemkata.idmaterifonemkata)).scalar() or 0) + \
                                    (self.db.query(func.count(Materifonemkalimat.idmaterifonemkalimat)).scalar() or 0)
        total_exam_phoneme = self.db.query(func.count(func.distinct(Materiujian.kategori))).scalar() or 0
        total_interview = self.db.query(func.count(Materiinterview.idmateriinterview)).scalar() or 0
        
        return {
            "statistics": {
                "totalTalent": total_talent,
                "totalPronunciationMaterial": total_pronunciation_material,
                "totalExamPhonemMaterial": total_exam_phoneme,
                "totalInterviewQuestion": total_interview
            }
        }

    def get_recent_pronunciation_activities(self, limit: int = 10, days_back: int = 30) -> Dict[str, Any]:
        try:
            limit = self.validate_activity_limit(limit)
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            phoneme_query = self.db.query(
                Hasillatihanfonem.idhasilfonem,
                Hasillatihanfonem.idtalent,
                Hasillatihanfonem.typelatihan,
                Hasillatihanfonem.idsoal,
                Hasillatihanfonem.nilai,
                Hasillatihanfonem.waktulatihan,
                Talent.nama.label('talent_name')
            ).join(
                Talent, Talent.idtalent == Hasillatihanfonem.idtalent
            ).filter(
                Hasillatihanfonem.waktulatihan >= cutoff_date
            ).order_by(desc(Hasillatihanfonem.waktulatihan)).limit(limit * 2)

            phoneme_results = phoneme_query.all()

            exam_query = self.db.query(
                Ujianfonem.idujian,
                Ujianfonem.idtalent,
                Ujianfonem.kategori,
                Ujianfonem.nilai,
                Ujianfonem.waktuujian,
                Talent.nama.label('talent_name')
            ).join(
                Talent, Talent.idtalent == Ujianfonem.idtalent
            ).filter(
                Ujianfonem.waktuujian >= cutoff_date
            ).order_by(desc(Ujianfonem.waktuujian)).limit(limit * 2)

            exam_results = exam_query.all()

            all_activities = []
            
            for activity in phoneme_results:
                try:
                    category = "Unknown"
                    activity_type = "Phoneme Practice"
                    
                    if activity.typelatihan == 'Word':
                        activity_type = "Word Practice"
                        word_cat = self.db.query(Materifonemkata.kategori).filter(
                            Materifonemkata.idmaterifonemkata == activity.idsoal
                        ).first()
                        if word_cat:
                            category = word_cat.kategori
                    elif activity.typelatihan == 'Sentence':
                        activity_type = "Sentence Practice"
                        sentence_cat = self.db.query(Materifonemkalimat.kategori).filter(
                            Materifonemkalimat.idmaterifonemkalimat == activity.idsoal
                        ).first()
                        if sentence_cat:
                            category = sentence_cat.kategori
                    
                    best_score = activity.nilai
                    try:
                        if category != "Unknown":
                            if activity.typelatihan == 'Word':
                                best_query = self.db.query(func.max(Hasillatihanfonem.nilai)).join(
                                    Materifonemkata, Materifonemkata.idmaterifonemkata == Hasillatihanfonem.idsoal
                                ).filter(
                                    Hasillatihanfonem.idtalent == activity.idtalent,
                                    Materifonemkata.kategori == category
                                )
                                best_result = best_query.scalar()
                                if best_result:
                                    best_score = best_result
                            elif activity.typelatihan == 'Sentence':
                                best_query = self.db.query(func.max(Hasillatihanfonem.nilai)).join(
                                    Materifonemkalimat, Materifonemkalimat.idmaterifonemkalimat == Hasillatihanfonem.idsoal
                                ).filter(
                                    Hasillatihanfonem.idtalent == activity.idtalent,
                                    Materifonemkalimat.kategori == category
                                )
                                best_result = best_query.scalar()
                                if best_result:
                                    best_score = best_result
                    except Exception:
                        pass
                    
                    all_activities.append({
                        'talent_id': activity.idtalent,
                        'talent_name': activity.talent_name,
                        'activity_type': activity_type,
                        'category': category,
                        'latest_score': activity.nilai or 0,
                        'best_score': best_score or 0,
                        'activity_date': activity.waktulatihan
                    })
                except Exception:
                    continue

            for activity in exam_results:
                try:
                    best_score = activity.nilai
                    try:
                        best_query = self.db.query(func.max(Ujianfonem.nilai)).filter(
                            Ujianfonem.idtalent == activity.idtalent,
                            Ujianfonem.kategori == activity.kategori
                        )
                        best_result = best_query.scalar()
                        if best_result:
                            best_score = best_result
                    except Exception:
                        pass
                    
                    all_activities.append({
                        'talent_id': activity.idtalent,
                        'talent_name': activity.talent_name,
                        'activity_type': 'Phoneme Exam',
                        'category': activity.kategori or 'Unknown',
                        'latest_score': activity.nilai or 0,
                        'best_score': best_score or 0,
                        'activity_date': activity.waktuujian
                    })
                except Exception:
                    continue

            all_activities.sort(key=lambda x: x['activity_date'] if x['activity_date'] else datetime.min, reverse=True)
            recent_activities = all_activities[:limit]

            formatted_activities = []
            for activity in recent_activities:
                formatted_activities.append({
                    'talentId': activity['talent_id'],
                    'talentName': activity['talent_name'],
                    'activityType': activity['activity_type'],
                    'category': activity['category'],
                    'latestScore': f"{activity['latest_score']:.0f}%",
                    'bestScore': f"{activity['best_score']:.0f}%",
                    'lastActivity': TimestampHelper.format_utc_to_wib_str(activity['activity_date'])
                })

            return {
                "recentPronunciationActivities": formatted_activities,
                "totalActivities": len(all_activities),
                "dateRange": f"Last {days_back} days",
                "requestedLimit": limit,
                "actualReturned": len(formatted_activities)
            }

        except Exception as e:
            return {
                "recentPronunciationActivities": [],
                "totalActivities": 0,
                "dateRange": f"Last {days_back} days",
                "requestedLimit": limit,
                "actualReturned": 0,
                "error": str(e)
            }

    def get_recent_speaking_activities(self, limit: int = 10, days_back: int = 30) -> Dict[str, Any]:
        """Get recent speaking activities - BACK TO WORKING VERSION"""
        try:
            limit = self.validate_activity_limit(limit)
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            conv_query = self.db.query(
                Hasillatihanpercakapan.idhasilpercakapan,
                Hasillatihanpercakapan.idtalent,
                Hasillatihanpercakapan.wpm,
                Hasillatihanpercakapan.grammar,
                Hasillatihanpercakapan.waktulatihan,
                Talent.nama.label('talent_name')
            ).join(
                Talent, Talent.idtalent == Hasillatihanpercakapan.idtalent
            ).filter(
                Hasillatihanpercakapan.waktulatihan >= cutoff_date
            ).order_by(desc(Hasillatihanpercakapan.waktulatihan)).limit(limit * 2)

            conv_results = conv_query.all()

            interview_query = self.db.query(
                Hasillatihaninterview.idhasilinterview,
                Hasillatihaninterview.idtalent,
                Hasillatihaninterview.wpm,
                Hasillatihaninterview.feedback,
                Hasillatihaninterview.waktulatihan,
                Talent.nama.label('talent_name')
            ).join(
                Talent, Talent.idtalent == Hasillatihaninterview.idtalent
            ).filter(
                Hasillatihaninterview.waktulatihan >= cutoff_date
            ).order_by(desc(Hasillatihaninterview.waktulatihan)).limit(limit * 2)

            interview_results = interview_query.all()

            all_activities = []
            
            for activity in conv_results:
                try:
                    grammar_preview = activity.grammar or "No grammar data"
                    if len(grammar_preview) > 50:
                        grammar_preview = grammar_preview[:47] + "..."
                    
                    all_activities.append({
                        'talent_id': activity.idtalent,
                        'talent_name': activity.talent_name,
                        'activity_type': 'Conversation',
                        'wpm': activity.wpm or 0,
                        'grammar_feedback': grammar_preview,
                        'activity_date': activity.waktulatihan
                    })
                except Exception:
                    continue

            for activity in interview_results:
                try:
                    feedback_preview = activity.feedback or "No feedback available"
                    if len(feedback_preview) > 50:
                        feedback_preview = feedback_preview[:47] + "..."
                    
                    all_activities.append({
                        'talent_id': activity.idtalent,
                        'talent_name': activity.talent_name,
                        'activity_type': 'Interview',
                        'wpm': activity.wpm or 0,
                        'grammar_feedback': feedback_preview,
                        'activity_date': activity.waktulatihan
                    })
                except Exception:
                    continue

            all_activities.sort(key=lambda x: x['activity_date'] if x['activity_date'] else datetime.min, reverse=True)
            recent_activities = all_activities[:limit]

            formatted_activities = []
            for activity in recent_activities:
                formatted_activities.append({
                    'talentId': activity['talent_id'],
                    'talentName': activity['talent_name'],
                    'activityType': activity['activity_type'],
                    'wpm': self.format_wpm(activity['wpm']),
                    'grammarFeedback': activity['grammar_feedback'],
                    'lastActivity': TimestampHelper.format_utc_to_wib_str(activity['activity_date'])
                })

            return {
                "recentSpeakingActivities": formatted_activities,
                "totalActivities": len(all_activities),
                "dateRange": f"Last {days_back} days",
                "requestedLimit": limit,
                "actualReturned": len(formatted_activities)
            }

        except Exception as e:
            return {
                "recentSpeakingActivities": [],
                "totalActivities": 0,
                "dateRange": f"Last {days_back} days",
                "requestedLimit": limit,
                "actualReturned": 0,
                "error": str(e)
            }

    def get_recent_activities(self, limit: int = 10, days_back: int = 30) -> Dict[str, Any]:
        """Get combined recent activities - BACK TO WORKING VERSION"""
        try:
            pronunciation_data = self.get_recent_pronunciation_activities(limit, days_back)
            speaking_data = self.get_recent_speaking_activities(limit, days_back)
            
            total_activities = pronunciation_data.get("totalActivities", 0) + speaking_data.get("totalActivities", 0)
            has_error = "error" in pronunciation_data or "error" in speaking_data
            
            result = {
                "pronunciationActivities": pronunciation_data.get("recentPronunciationActivities", []),
                "speakingActivities": speaking_data.get("recentSpeakingActivities", []),
                "totalActivities": total_activities,
                "dateRange": f"Last {days_back} days",
                "hasError": has_error,
                "requestedLimit": limit,
                "pronunciationLimit": pronunciation_data.get("actualReturned", 0),
                "speakingLimit": speaking_data.get("actualReturned", 0)
            }
            
            return result

        except Exception as e:
            return {
                "pronunciationActivities": [],
                "speakingActivities": [],
                "totalActivities": 0,
                "dateRange": f"Last {days_back} days",
                "hasError": True,
                "error": str(e),
                "requestedLimit": limit,
                "pronunciationLimit": 0,
                "speakingLimit": 0
            }
    
    def get_top_active_learners(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)

        query = self.db.query(Talent)
        if search and search.strip():
            query = query.filter(Talent.nama.ilike(f"%{search.strip()}%"))

        all_talents = query.all()

        talent_streaks = []
        for talent in all_talents:
            latihan_dates = self.db.query(Hasillatihanfonem.waktulatihan).filter(
                Hasillatihanfonem.idtalent == talent.idtalent
            ).all()
            dates = [d[0].date() for d in latihan_dates] if latihan_dates else []
            
            highest_streak, current_streak = self._calculate_streaks(dates)

            talent_streaks.append({
                "talent": talent,
                "highest_streak": highest_streak,
                "current_streak": current_streak
            })

        talent_streaks.sort(
            key=lambda x: (-x["current_streak"], -x["highest_streak"], x["talent"].nama)
        )

        total_items = len(talent_streaks)
        offset, limit = PaginationHelper.get_offset_limit(page, size)
        paginated_talents = talent_streaks[offset:offset + limit]

        result = []
        for i, talent_data in enumerate(paginated_talents, start=offset + 1):
            result.append({
                "no": i,
                "id": talent_data["talent"].idtalent,
                "talentName": talent_data["talent"].nama,
                "email": talent_data["talent"].email,
                "highestStreak": f"{talent_data['highest_streak']} Days",
                "currentStreak": f"{talent_data['current_streak']} Days"
            })

        return paginate_learners_list(result, total_items, page, size)

    def get_highest_scoring_learners_phoneme_material(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)

        total_words = self.db.query(Materifonemkata).count()

        talent_stats_query = self.db.query(
            Hasillatihanfonem.idtalent,
            func.count(func.distinct(Hasillatihanfonem.idsoal)).label('attempted_words'),
            func.avg(Hasillatihanfonem.nilai).label('avg_score'),
            func.max(Hasillatihanfonem.nilai).label('best_score')
        ).filter(
            Hasillatihanfonem.typelatihan == 'Word'
        ).group_by(Hasillatihanfonem.idtalent).subquery()

        query = self.db.query(
            Talent.idtalent,
            Talent.nama,
            Talent.email,
            func.coalesce(talent_stats_query.c.attempted_words, 0).label('attempted_words'),
            func.coalesce(talent_stats_query.c.avg_score, 0).label('avg_score'),
            func.coalesce(talent_stats_query.c.best_score, 0).label('best_score')
        ).outerjoin(
            talent_stats_query, Talent.idtalent == talent_stats_query.c.idtalent
        )

        if search and search.strip():
            query = query.filter(Talent.nama.ilike(f"%{search.strip()}%"))

        all_results = query.all()

        sorted_results = sorted(
            all_results,
            key=lambda x: (-x.avg_score, -x.attempted_words, x.nama)
        )

        total_items = len(sorted_results)
        offset, limit = PaginationHelper.get_offset_limit(page, size)
        paginated_results = sorted_results[offset:offset + limit]

        result = []
        for i, talent_data in enumerate(paginated_results, start=offset + 1):
            completion_rate = (talent_data.attempted_words / total_words * 100) if total_words > 0 else 0
            
            result.append({
                "no": i,
                "id": talent_data.idtalent,
                "talentName": talent_data.nama,
                "overallCompletion": f"{talent_data.attempted_words}/{total_words}",
                "overallPercentage": f"{talent_data.avg_score:.0f}%",
                "completionRate": f"{completion_rate:.0f}%"
            })
            
        category_info = {
            "activeTab": "phoneme_material_exercise",
            "availableTabs": ["phoneme_material_exercise", "phoneme_exercise", "phoneme_exam", "conversation", "interview"],
            "sortingCriteria": "Average Score (desc) → Attempted Words (desc) → Name (asc)"
        }
        return paginate_learners_list(result, total_items, page, size, category_info)

    def get_highest_scoring_learners_phoneme_exercise(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)

        total_sentences = self.db.query(Materifonemkalimat).count()
        
        talent_stats_query = self.db.query(
            Hasillatihanfonem.idtalent,
            func.count(func.distinct(Hasillatihanfonem.idsoal)).label('attempted_sentences'),
            func.avg(Hasillatihanfonem.nilai).label('avg_score'),
            func.max(Hasillatihanfonem.nilai).label('best_score')
        ).filter(
            Hasillatihanfonem.typelatihan == 'Sentence'
        ).group_by(Hasillatihanfonem.idtalent).subquery()

        query = self.db.query(
            Talent.idtalent,
            Talent.nama,
            Talent.email,
            func.coalesce(talent_stats_query.c.attempted_sentences, 0).label('attempted_sentences'),
            func.coalesce(talent_stats_query.c.avg_score, 0).label('avg_score'),
            func.coalesce(talent_stats_query.c.best_score, 0).label('best_score')
        ).outerjoin(
            talent_stats_query, Talent.idtalent == talent_stats_query.c.idtalent
        )

        if search and search.strip():
            query = query.filter(Talent.nama.ilike(f"%{search.strip()}%"))

        all_results = query.all()
        sorted_results = sorted(
            all_results,
            key=lambda x: (-x.avg_score, -x.attempted_sentences, x.nama)
        )

        total_items = len(sorted_results)
        offset, limit = PaginationHelper.get_offset_limit(page, size)
        paginated_results = sorted_results[offset:offset + limit]

        result = []
        for i, talent_data in enumerate(paginated_results, start=offset + 1):
            completion_rate = (talent_data.attempted_sentences / total_sentences * 100) if total_sentences > 0 else 0
            
            result.append({
                "no": i,
                "id": talent_data.idtalent,
                "talentName": talent_data.nama,
                "overallCompletion": f"{talent_data.attempted_sentences}/{total_sentences}",
                "overallPercentage": f"{talent_data.avg_score:.0f}%",
                "completionRate": f"{completion_rate:.0f}%"
            })

        category_info = {
            "activeTab": "phoneme_exercise",
            "availableTabs": ["phoneme_material_exercise", "phoneme_exercise", "phoneme_exam", "conversation", "interview"],
            "sortingCriteria": "Average Score (desc) → Attempted Sentences (desc) → Name (asc)"
        }
        return paginate_learners_list(result, total_items, page, size, category_info)

    def get_highest_scoring_learners_phoneme_exam(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        page, size = PaginationHelper.validate_pagination_params(page, size)

        total_exam_categories = self.db.query(func.count(func.distinct(Materiujian.kategori))).scalar() or 0
        
        talent_exam_stats = self.db.query(
            Ujianfonem.idtalent,
            func.count(func.distinct(Ujianfonem.kategori)).label('categories_attempted'),
            func.avg(Ujianfonem.nilai).label('avg_score'),
            func.max(Ujianfonem.nilai).label('best_score'),
            func.count(Ujianfonem.idujian).label('total_attempts')
        ).group_by(Ujianfonem.idtalent).subquery()

        query = self.db.query(
            Talent.idtalent,
            Talent.nama,
            Talent.email,
            func.coalesce(talent_exam_stats.c.categories_attempted, 0).label('categories_attempted'),
            func.coalesce(talent_exam_stats.c.avg_score, 0).label('avg_score'),
            func.coalesce(talent_exam_stats.c.best_score, 0).label('best_score'),
            func.coalesce(talent_exam_stats.c.total_attempts, 0).label('total_attempts')
        ).outerjoin(
            talent_exam_stats, Talent.idtalent == talent_exam_stats.c.idtalent
        )

        if search and search.strip():
            query = query.filter(Talent.nama.ilike(f"%{search.strip()}%"))

        all_results = query.all()
        
        sorted_results = sorted(
            all_results,
            key=lambda x: (-x.avg_score, -x.categories_attempted, x.nama)
        )

        total_items = len(sorted_results)
        offset, limit = PaginationHelper.get_offset_limit(page, size)
        paginated_results = sorted_results[offset:offset + limit]

        result = []
        for i, talent_data in enumerate(paginated_results, start=offset + 1):
            completion_rate = (talent_data.categories_attempted / total_exam_categories * 100) if total_exam_categories > 0 else 0
            
            result.append({
                "no": i,
                "id": talent_data.idtalent,
                "talentName": talent_data.nama,
                "overallCompletion": f"{talent_data.categories_attempted}/{total_exam_categories}",
                "overallPercentage": f"{talent_data.avg_score:.0f}%",
                "completionRate": f"{completion_rate:.0f}%",
                "totalAttempts": talent_data.total_attempts
            })

        category_info = {
            "activeTab": "phoneme_exam",
            "availableTabs": ["phoneme_material_exercise", "phoneme_exercise", "phoneme_exam", "conversation", "interview"],
            "sortingCriteria": "Average Score (desc) → Categories Attempted (desc) → Name (asc)"
        }
        return paginate_learners_list(result, total_items, page, size, category_info)

    def get_conversation_results(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        try:
            page, size = PaginationHelper.validate_pagination_params(page, size)

            talent_conv_stats = self.db.query(
                Hasillatihanpercakapan.idtalent,
                func.avg(Hasillatihanpercakapan.wpm).label('avg_wpm'),
                func.max(Hasillatihanpercakapan.wpm).label('best_wpm'),
                func.count(Hasillatihanpercakapan.idhasilpercakapan).label('total_attempts'),
                func.max(Hasillatihanpercakapan.waktulatihan).label('latest_attempt')
            ).group_by(Hasillatihanpercakapan.idtalent).subquery()
            
            query = self.db.query(
                Talent.idtalent,
                Talent.nama,
                Talent.email,
                func.coalesce(talent_conv_stats.c.avg_wpm, 0).label('avg_wpm'),
                func.coalesce(talent_conv_stats.c.best_wpm, 0).label('best_wpm'),
                func.coalesce(talent_conv_stats.c.total_attempts, 0).label('total_attempts'),
                talent_conv_stats.c.latest_attempt
            ).outerjoin(
                talent_conv_stats, Talent.idtalent == talent_conv_stats.c.idtalent
            )
            
            if search and search.strip():
                query = query.filter(Talent.nama.ilike(f"%{search.strip()}%"))

            all_results = query.all()

            sorted_results = sorted(
                all_results,
                key=lambda x: (-x.avg_wpm, -x.total_attempts, x.nama)
            )

            total_items = len(sorted_results)
            offset, limit = PaginationHelper.get_offset_limit(page, size)
            paginated_results = sorted_results[offset:offset + limit]

            result = []
            for i, talent_data in enumerate(paginated_results, start=offset + 1):
                latest_conversation = None
                if talent_data.latest_attempt:
                    latest_conversation = self.db.query(
                        Hasillatihanpercakapan.grammar,
                        Hasillatihanpercakapan.waktulatihan
                    ).filter(
                        Hasillatihanpercakapan.idtalent == talent_data.idtalent
                    ).order_by(desc(Hasillatihanpercakapan.waktulatihan)).first()
                
                result.append({
                    "no": i,
                    "id": talent_data.idtalent,
                    "talentName": talent_data.nama,
                    "wpm": self.format_wpm(talent_data.avg_wpm),
                    "grammer": latest_conversation.grammar if latest_conversation and latest_conversation.grammar else "No data",
                    "date": latest_conversation.waktulatihan.strftime("%Y-%m-%d") if latest_conversation and latest_conversation.waktulatihan else "N/A",
                    "totalAttempts": talent_data.total_attempts or 0
                })

            category_info = {
                "activeTab": "conversation",
                "availableTabs": ["phoneme_material_exercise", "phoneme_exercise", "phoneme_exam", "conversation", "interview"],
                "sortingCriteria": "Average WPM (desc) → Total Attempts (desc) → Name (asc)"
            }
            
            return paginate_learners_list(result, total_items, page, size, category_info)
            
        except Exception as e:
            return {
                "data": {
                    "learners": [],
                    "pagination": {
                        "currentPage": page,
                        "totalPages": 0,
                        "totalRecords": 0,
                        "showing": "Error loading data"
                    }
                },
                "message": f"Error loading conversation results: {str(e)}"
            }

    def get_interview_results(self, search: Optional[str] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        try:
            page, size = PaginationHelper.validate_pagination_params(page, size)
            
            talent_interview_stats = self.db.query(
                Hasillatihaninterview.idtalent,
                func.avg(Hasillatihaninterview.wpm).label('avg_wpm'),
                func.max(Hasillatihaninterview.wpm).label('best_wpm'),
                func.count(Hasillatihaninterview.idhasilinterview).label('total_attempts'),
                func.max(Hasillatihaninterview.waktulatihan).label('latest_attempt')
            ).group_by(Hasillatihaninterview.idtalent).subquery()
            
            query = self.db.query(
                Talent.idtalent,
                Talent.nama,
                Talent.email,
                func.coalesce(talent_interview_stats.c.avg_wpm, 0).label('avg_wpm'),
                func.coalesce(talent_interview_stats.c.best_wpm, 0).label('best_wpm'),
                func.coalesce(talent_interview_stats.c.total_attempts, 0).label('total_attempts'),
                talent_interview_stats.c.latest_attempt
            ).outerjoin(
                talent_interview_stats, Talent.idtalent == talent_interview_stats.c.idtalent
            )
            
            if search and search.strip():
                query = query.filter(Talent.nama.ilike(f"%{search.strip()}%"))

            all_results = query.all()

            sorted_results = sorted(
                all_results,
                key=lambda x: (-x.avg_wpm, -x.total_attempts, x.nama)
            )

            total_items = len(sorted_results)
            offset, limit = PaginationHelper.get_offset_limit(page, size)
            paginated_results = sorted_results[offset:offset + limit]

            result = []
            for i, talent_data in enumerate(paginated_results, start=offset + 1):
                latest_interview = None
                if talent_data.latest_attempt:
                    latest_interview = self.db.query(
                        Hasillatihaninterview.feedback,
                        Hasillatihaninterview.waktulatihan
                    ).filter(
                        Hasillatihaninterview.idtalent == talent_data.idtalent
                    ).order_by(desc(Hasillatihaninterview.waktulatihan)).first()

                feedback_preview = "No feedback available"
                if latest_interview and latest_interview.feedback:
                    feedback_text = latest_interview.feedback
                    if len(feedback_text) > 50:
                        feedback_preview = feedback_text[:50] + "..."
                    else:
                        feedback_preview = feedback_text
                
                result.append({
                    "no": i,
                    "id": talent_data.idtalent,
                    "talentName": talent_data.nama,
                    "wpm": self.format_wpm(talent_data.avg_wpm),
                    "feedback": feedback_preview,
                    "date": latest_interview.waktulatihan.strftime("%Y-%m-%d") if latest_interview and latest_interview.waktulatihan else "N/A",
                    "totalAttempts": talent_data.total_attempts or 0
                })

            category_info = {
                "activeTab": "interview",
                "availableTabs": ["phoneme_material_exercise", "phoneme_exercise", "phoneme_exam", "conversation", "interview"],
                "sortingCriteria": "Average WPM (desc) → Total Attempts (desc) → Name (asc)"
            }
            
            return paginate_learners_list(result, total_items, page, size, category_info)
            
        except Exception as e:
            return {
                "data": {
                    "learners": [],
                    "pagination": {
                        "currentPage": page,
                        "totalPages": 0,
                        "totalRecords": 0,
                        "showing": "Error loading data"
                    }
                },
                "message": f"Error loading interview results: {str(e)}"
            }

    def _calculate_streaks(self, training_dates: List[datetime.date]) -> Tuple[int, int]:
        if not training_dates:
            return 0, 0
            
        training_dates = sorted(list(set(training_dates)), reverse=True)
        
        highest_streak = 0
        if training_dates:
            temp_streak = 1
            for i in range(len(training_dates) - 1):
                if (training_dates[i] - training_dates[i+1]).days == 1:
                    temp_streak += 1
                else:
                    highest_streak = max(highest_streak, temp_streak)
                    temp_streak = 1
            highest_streak = max(highest_streak, temp_streak)
        
        current_streak = 0
        today = datetime.now().date()
        
        if training_dates:
            last_training = training_dates[0]
            
            if last_training == today or last_training == today - timedelta(days=1):
                current_streak = 1
                for i in range(len(training_dates) - 1):
                    if (training_dates[i] - training_dates[i+1]).days == 1:
                        current_streak += 1
                    else:
                        break

        return highest_streak, current_streak

    def update_admin_profile(self, admin_id: int, nama: str, email: str) -> Dict[str, Any]:
        admin = self.db.query(Manajemen).filter(Manajemen.idmanajemen == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        admin.namamanajemen = nama
        admin.email = email
        self.db.commit()
        self.db.refresh(admin)

        return {"message": "Admin profile updated successfully"}

    def change_admin_password(self, admin_id: int, new_password: str) -> Dict[str, Any]:
        admin = self.db.query(Manajemen).filter(Manajemen.idmanajemen == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password minimal 6 karakter")

        hashed_password = pwd_context.hash(new_password)
        admin.password = hashed_password

        self.db.commit()
        return {"message": "Password updated successfully"}

    def get_admin_profile(self, admin_id: int) -> Dict[str, Any]:
        admin = self.db.query(Manajemen).filter(Manajemen.idmanajemen == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        return {
            "id": admin.idmanajemen,
            "nama": admin.namamanajemen,
            "email": admin.email
        }