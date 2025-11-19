from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, String, and_
from sqlalchemy.sql import literal_column
from datetime import datetime, timedelta
from database import get_db
from models import (
    Hasillatihanfonem, Hasillatihanpercakapan, Hasillatihaninterview,
    Ujianfonem, Detailujianfonem, Talent
)
from controller.AuthController import get_current_user
from utils.timestamp_helper import TimestampHelper

homeactivityrouter = APIRouter(prefix="/home", tags=["home"])

@homeactivityrouter.get("/summary")
def get_home_summary(authorization: str = Header(None), db: Session = Depends(get_db)):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    talent = db.query(Talent).filter(Talent.idtalent == idtalent).first()
    nama_user = talent.nama if talent else "User"

    # === 1. Recent Activities ===
    phoneme = db.query(
        Hasillatihanfonem.idsoal.label("id"),
        Hasillatihanfonem.waktulatihan,
        Hasillatihanfonem.nilai.label("score"),
        literal_column("'Phoneme Training'", type_=String).label("title"),
        literal_column("'phoneme'", type_=String).label("type"),
        Hasillatihanfonem.typelatihan.label("category"),
    ).filter(Hasillatihanfonem.idtalent == idtalent) \
     .order_by(desc(Hasillatihanfonem.waktulatihan)).limit(10).all()

    conversation = db.query(
        Hasillatihanpercakapan.idmateripercakapan.label("id"),
        Hasillatihanpercakapan.waktulatihan,
        Hasillatihanpercakapan.wpm.label("score"),
        literal_column("'Conversation Practice'", type_=String).label("title"),
        literal_column("'conversation'", type_=String).label("type"),
        literal_column("'Speaking'", type_=String).label("category"),
    ).filter(Hasillatihanpercakapan.idtalent == idtalent) \
     .order_by(desc(Hasillatihanpercakapan.waktulatihan)).limit(10).all()

    interview = db.query(
        Hasillatihaninterview.idhasilinterview.label("id"),
        Hasillatihaninterview.waktulatihan,
        Hasillatihaninterview.wpm.label("score"),
        literal_column("'Interview Practice'", type_=String).label("title"),
        literal_column("'interview'", type_=String).label("type"),
        literal_column("'Speaking'", type_=String).label("category"),
    ).filter(Hasillatihaninterview.idtalent == idtalent) \
     .order_by(desc(Hasillatihaninterview.waktulatihan)).limit(10).all()

    combined = phoneme + conversation + interview
    combined_sorted = sorted(combined, key=lambda x: x.waktulatihan, reverse=True)
    top_10 = combined_sorted[:10]

    activities_result = [
        {
            "id": item.id,
            "title": item.title,
            "type": item.type,
            "category": item.category,
            "score": round(float(item.score), 1) if item.score else 0.0,
            "date": item.waktulatihan.strftime("%d %b %Y"),
            "time": item.waktulatihan.strftime("%H:%M"),
            "waktulatihan": TimestampHelper.format_timestamp(item.waktulatihan),
        }
        for item in top_10
    ]

    # === 2. Learning Progress Summary ===
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Weekly progress
    phoneme_week = db.query(func.count(Hasillatihanfonem.idhasilfonem)).filter(
        and_(Hasillatihanfonem.idtalent == idtalent, 
             Hasillatihanfonem.waktulatihan >= week_ago)
    ).scalar() or 0

    conversation_week = db.query(func.count(Hasillatihanpercakapan.idhasilpercakapan)).filter(
        and_(Hasillatihanpercakapan.idtalent == idtalent, 
             Hasillatihanpercakapan.waktulatihan >= week_ago)
    ).scalar() or 0

    interview_week = db.query(func.count(Hasillatihaninterview.idhasilinterview)).filter(
        and_(Hasillatihaninterview.idtalent == idtalent, 
             Hasillatihaninterview.waktulatihan >= week_ago)
    ).scalar() or 0

    total_activities_week = phoneme_week + conversation_week + interview_week

    # Average scores for each type
    avg_phoneme_score = db.query(func.avg(Hasillatihanfonem.nilai)).filter(
        Hasillatihanfonem.idtalent == idtalent
    ).scalar()

    avg_conversation_wpm = db.query(func.avg(Hasillatihanpercakapan.wpm)).filter(
        Hasillatihanpercakapan.idtalent == idtalent
    ).scalar()

    avg_interview_wpm = db.query(func.avg(Hasillatihaninterview.wpm)).filter(
        Hasillatihaninterview.idtalent == idtalent
    ).scalar()

    # === 3. Exam Summary ===
    latest_exam = db.query(Ujianfonem).filter(
        Ujianfonem.idtalent == idtalent,
    ).order_by(desc(Ujianfonem.waktuujian)).first()

    total_exam = db.query(func.count(Ujianfonem.idujian)).filter(
        Ujianfonem.idtalent == idtalent,
        Ujianfonem.nilai != None 
    ).scalar()

    average_score = db.query(func.avg(Ujianfonem.nilai)).filter(
        Ujianfonem.idtalent == idtalent,
    ).scalar()

    last_exam_days_ago = None
    if latest_exam:
        delta = datetime.utcnow().date() - latest_exam.waktuujian.date()
        last_exam_days_ago = delta.days

    # === 4. Streak Information ===
    # Calculate learning streak (consecutive days with activities)
    streak_days = 0
    current_date = datetime.utcnow().date()
    
    for i in range(30):  # Check last 30 days
        check_date = current_date - timedelta(days=i)
        start_of_day = datetime.combine(check_date, datetime.min.time())
        end_of_day = datetime.combine(check_date, datetime.max.time())
        
        has_activity = db.query(
            db.query(Hasillatihanfonem).filter(
                and_(Hasillatihanfonem.idtalent == idtalent,
                     Hasillatihanfonem.waktulatihan >= start_of_day,
                     Hasillatihanfonem.waktulatihan <= end_of_day)
            ).exists()
        ).scalar()
        
        if not has_activity:
            has_activity = db.query(
                db.query(Hasillatihanpercakapan).filter(
                    and_(Hasillatihanpercakapan.idtalent == idtalent,
                         Hasillatihanpercakapan.waktulatihan >= start_of_day,
                         Hasillatihanpercakapan.waktulatihan <= end_of_day)
                ).exists()
            ).scalar()
        
        if not has_activity:
            has_activity = db.query(
                db.query(Hasillatihaninterview).filter(
                    and_(Hasillatihaninterview.idtalent == idtalent,
                         Hasillatihaninterview.waktulatihan >= start_of_day,
                         Hasillatihaninterview.waktulatihan <= end_of_day)
                ).exists()
            ).scalar()
        
        if has_activity:
            streak_days += 1
        else:
            break

    # === 5. Quick Stats ===
    total_phoneme_sessions = db.query(func.count(Hasillatihanfonem.idhasilfonem)).filter(
        Hasillatihanfonem.idtalent == idtalent
    ).scalar() or 0

    total_conversation_sessions = db.query(func.count(Hasillatihanpercakapan.idhasilpercakapan)).filter(
        Hasillatihanpercakapan.idtalent == idtalent
    ).scalar() or 0

    total_interview_sessions = db.query(func.count(Hasillatihaninterview.idhasilinterview)).filter(
        Hasillatihaninterview.idtalent == idtalent
    ).scalar() or 0

    return {
        "user": {
            "id": idtalent,
            "name": nama_user,
        },
        "learning_streak": {
            "current_streak": streak_days,
            "this_week_activities": total_activities_week
        },
        "quick_stats": {
            "total_training_sessions": total_phoneme_sessions + total_conversation_sessions + total_interview_sessions,
            "avg_phoneme_score": round(avg_phoneme_score, 1) if avg_phoneme_score else None,
            "avg_speaking_wpm": round((avg_conversation_wpm + avg_interview_wpm) / 2, 1) if avg_conversation_wpm and avg_interview_wpm else None,
            "phoneme_sessions": total_phoneme_sessions,
            "speaking_sessions": total_conversation_sessions + total_interview_sessions
        },
        "recent_activities": {
            "total": len(activities_result),
            "data": activities_result
        },
        "exam_summary": {
            "latest_exam_score": latest_exam.nilai if latest_exam else None,
            "total_exams": total_exam or 0,
            "average_exam_score": round(average_score, 2) if average_score else None,
            "last_exam_days_ago": last_exam_days_ago
        }
    }