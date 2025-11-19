from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from models import Hasillatihanpercakapan, Materipercakapan
from models import Hasillatihaninterview
from models import Hasillatihanfonem, Materifonemkata, Materifonemkalimat
from models import Ujianfonem, Detailujianfonem, Materiujiankalimat
from database import get_db
from controller.AuthController import get_current_user
import base64
import json
from utils.timestamp_helper import TimestampHelper

historyrouter = APIRouter(prefix="/history", tags=["history"])

@historyrouter.get("/phoneme")
def get_phoneme_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    base_query = db.query(Hasillatihanfonem).filter(
        Hasillatihanfonem.idtalent == idtalent,
        Hasillatihanfonem.waktulatihan >= seven_days_ago
    )

    total_items = base_query.count()

    offset = (page - 1) * size
    latihan_list = base_query.order_by(Hasillatihanfonem.waktulatihan.desc()) \
        .offset(offset).limit(size).all()

    result = []
    for lat in latihan_list:
        soal = None

        if lat.typelatihan == 'Word':
            soal_obj = db.query(Materifonemkata).filter_by(idmaterifonemkata=lat.idsoal).first()
            soal = soal_obj.kata if soal_obj else None
        elif lat.typelatihan == 'Sentence':
            soal_obj = db.query(Materifonemkalimat).filter_by(idmaterifonemkalimat=lat.idsoal).first()
            soal = soal_obj.kalimat if soal_obj else None

        result.append({
            "idsoal": lat.idsoal,
            "typelatihan": lat.typelatihan,
            "soal": soal,
            "nilai": lat.nilai,
            "waktulatihan": TimestampHelper.format_timestamp(lat.waktulatihan),
            "phoneme_comparison": lat.phoneme_comparison  # ← tambahkan ini
        })

    return {
        "page": page,
        "size": size,
        "total_items": total_items,
        "data": result
    }



@historyrouter.get("/conversation")
def get_conversation_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    base_query = db.query(Hasillatihanpercakapan).filter(
        Hasillatihanpercakapan.idtalent == idtalent,
        Hasillatihanpercakapan.waktulatihan >= seven_days_ago
    )

    total_items = base_query.count()
    offset = (page - 1) * size

    latihan_list = base_query.order_by(Hasillatihanpercakapan.waktulatihan.desc()) \
        .offset(offset).limit(size).all()

    result = []
    for lat in latihan_list:
        topic = db.query(Materipercakapan.topic).filter(
            Materipercakapan.idmateripercakapan == lat.idmateripercakapan
        ).scalar()
        result.append({
            "idmateripercakapan": lat.idmateripercakapan,
            "topic": topic,
            "wpm": lat.wpm,
            "grammar": lat.grammar,
            "waktulatihan": TimestampHelper.format_timestamp(lat.waktulatihan),
        })

    return {
        "page": page,
        "size": size,
        "total_items": total_items,
        "data": result
    }



@historyrouter.get("/interview")
def get_interview_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    base_query = db.query(Hasillatihaninterview).filter(
        Hasillatihaninterview.idtalent == idtalent,
        Hasillatihaninterview.waktulatihan >= seven_days_ago
    )

    total_items = base_query.count()
    offset = (page - 1) * size

    latihan_list = base_query.order_by(Hasillatihaninterview.waktulatihan.desc()) \
        .offset(offset).limit(size).all()

    result = [
        {
            "idhasilinterview": lat.idhasilinterview,
            "wpm": lat.wpm,
            "grammar": lat.grammar,
            "feedback": lat.feedback,
            "waktulatihan": TimestampHelper.format_timestamp(lat.waktulatihan),
        }
        for lat in latihan_list
    ]

    return {
        "page": page,
        "size": size,
        "total_items": total_items,
        "data": result
    }


@historyrouter.get("/exam")
def get_phoneme_exam_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    base_query = db.query(Ujianfonem).filter(
        Ujianfonem.idtalent == idtalent,
        Ujianfonem.waktuujian >= seven_days_ago
    )

    total_items = base_query.count()
    offset = (page - 1) * size

    ujian_list = base_query.order_by(Ujianfonem.waktuujian.desc()) \
        .offset(offset).limit(size).all()

    result = []
    for ujian in ujian_list:
        # Ambil detail soal untuk setiap ujian
        detail_list = db.query(Detailujianfonem).filter(
            Detailujianfonem.idujian == ujian.idujian
        ).all()

        detail_items = []
        for det in detail_list:
            kalimat_soal = db.query(Materiujiankalimat.kalimat).filter(
                Materiujiankalimat.idmateriujiankalimat == det.idsoal
            ).scalar()

            detail_items.append({
                "idsoal": det.idsoal,
                "kalimat": kalimat_soal,
                "nilai": det.nilai,
                "updated_at": det.updated_at.isoformat() if det.updated_at else None
            })

        result.append({
            "idujian": ujian.idujian,
            "kategori": ujian.kategori,
            "nilai_total": ujian.nilai,
            "waktuujian": TimestampHelper.format_timestamp(ujian.waktuujian),
            "updated_at": TimestampHelper.format_timestamp(ujian.updated_at),
            "details": detail_items
        })

    return {
        "page": page,
        "size": size,
        "total_items": total_items,
        "data": result
    }