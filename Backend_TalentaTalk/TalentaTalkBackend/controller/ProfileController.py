# controller/ProfileController.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import (
    Talent,
    Ujianfonem,
    Hasillatihanfonem,
    Hasillatihanpercakapan,
    Hasillatihaninterview,
    Materifonemkata,
    Materifonemkalimat
)
from datetime import datetime, timedelta

def calculate_streaks(training_dates):
    if not training_dates:
        return 0, 0
    training_dates = sorted(set([d.date() for d in training_dates]), reverse=True)

    # Highest streak
    highest = 0
    current = 0
    temp = 1

    for i in range(1, len(training_dates)):
        if (training_dates[i - 1] - training_dates[i]) == timedelta(days=1):
            temp += 1
        else:
            highest = max(highest, temp)
            temp = 1
    highest = max(highest, temp)

    # Current streak (counting back from today)
    today = datetime.now().date()
    current = 0
    while today in training_dates:
        current += 1
        today -= timedelta(days=1)

    return highest, current

def get_profile_summary(db: Session, idtalent: int):
    talent = db.query(Talent).filter(Talent.idtalent == idtalent).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent tidak ditemukan")

    pretest_score = talent.pretest_score

    highest_exam = db.query(func.max(Ujianfonem.nilai))\
        .filter(Ujianfonem.idtalent == idtalent).scalar()

    last_test = db.query(Ujianfonem)\
        .filter(Ujianfonem.idtalent == idtalent)\
        .order_by(Ujianfonem.waktuujian.desc()).first()
    last_test_time = last_test.waktuujian.isoformat() if last_test else None

    last_test = db.query(Ujianfonem)\
        .filter(Ujianfonem.idtalent == idtalent)\
        .order_by(Ujianfonem.waktuujian.desc()).first()
    last_test_score = round(last_test.nilai, 2) if last_test and last_test.nilai is not None else None

    avg_pron = db.query(func.avg(Hasillatihanfonem.nilai))\
        .filter(Hasillatihanfonem.idtalent == idtalent).scalar()
    avg_pron = round(avg_pron, 2) if avg_pron else None

    avg_wpm_conversation = db.query(func.avg(Hasillatihanpercakapan.wpm))\
        .filter(Hasillatihanpercakapan.idtalent == idtalent).scalar()
    avg_wpm_conversation = round(avg_wpm_conversation, 2) if avg_wpm_conversation else None

    avg_wpm_interview = db.query(func.avg(Hasillatihaninterview.wpm))\
        .filter(Hasillatihaninterview.idtalent == idtalent).scalar()
    avg_wpm_interview = round(avg_wpm_interview, 2) if avg_wpm_interview else None

    total_foneme_materi = (
        db.query(func.count(Materifonemkata.idmaterifonemkata)).scalar() or 0
    ) + (
        db.query(func.count(Materifonemkalimat.idmaterifonemkalimat)).scalar() or 0
    )

    total_foneme_selesai = db.query(func.count(func.distinct(Hasillatihanfonem.idsoal)))\
        .filter(Hasillatihanfonem.idtalent == idtalent).scalar() or 0

    total_conversation_done = db.query(func.count(func.distinct(Hasillatihanpercakapan.idhasilpercakapan)))\
        .filter(Hasillatihanpercakapan.idtalent == idtalent).scalar() or 0

    total_interview_done = db.query(func.count(Hasillatihaninterview.idhasilinterview))\
        .filter(Hasillatihaninterview.idtalent == idtalent).scalar() or 0

    latihan_dates = db.query(Hasillatihanfonem.waktulatihan).filter(
        Hasillatihanfonem.idtalent == idtalent
    ).all()
    date_list = [d[0] for d in latihan_dates]
    highest_streak, current_streak = calculate_streaks(date_list)

    return {
        "name": talent.nama,
        "jobTitle": "Talent",
        "email": talent.email,
        "lastTest": last_test_score,
        "pretestScore": pretest_score,
        "highestExam": highest_exam,
        "averagePronunciation": avg_pron,
        "averageWPMConversation": avg_wpm_conversation,
        "averageWPMInterview": avg_wpm_interview,
        "highestStreak": highest_streak,
        "currentStreak": current_streak,
        "activity": {
            "phonemeCompleted": total_foneme_selesai,
            "phonemeTotal": total_foneme_materi,
            "conversationCompleted": total_conversation_done,
            "interviewCompleted": total_interview_done
        }
    }
