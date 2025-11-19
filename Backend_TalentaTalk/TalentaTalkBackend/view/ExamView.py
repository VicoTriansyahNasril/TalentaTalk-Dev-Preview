#ExamView.py
from fastapi import APIRouter, Form, File, UploadFile, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Materiujian, Materiujiankalimat, Ujianfonem, Detailujianfonem
from controller.AuthController import get_current_user
from datetime import datetime
from controller.PhonemeRecognitionController import (
    audio_processor, text_to_ipa_gruut, analyze_pronunciation,
    create_enhanced_alignment, calculate_enhanced_accuracy, 
    format_enhanced_phoneme_response, get_phoneme_status, is_phoneme_similar
)
import asyncio
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

examrouter = APIRouter(prefix="/exam", tags=["exam"])

# Ambil semua ujian berdasarkan kategori
@examrouter.get("/by_kategori/{kategori}")
def get_materiujian_by_kategori(kategori: str, db: Session = Depends(get_db)):
    materi = db.query(Materiujian).filter(Materiujian.kategori == kategori).all()
    if not materi:
        return {"error": "Content not found"}
    return {"data": materi}

@examrouter.get("/exam_by_category/{category}")
async def list_exam_by_category(category: str, db: Session = Depends(get_db)):
    """Mendapatkan semua ujian berdasarkan kategori fonem dari database"""
    exams = db.query(Materiujian).filter(Materiujian.kategori == category).all()
    if exams:
        result = []
        for exam in exams:
            result.append({
                "idmateriujian": exam.idmateriujian,
                "kategori": exam.kategori
            })
        return {"category": category, "sentences": result}
    return {"message": f"No sentences found for category '{category}'"}

# Ambil semua kalimat berdasarkan ID ujian
@examrouter.get("/kalimat/{idujian}")
def get_kalimat_by_idujian(idujian: int, db: Session = Depends(get_db)):
    kalimat = db.query(Materiujiankalimat).filter(Materiujiankalimat.idujian == idujian).all()
    if not kalimat:
        return {"error": "Content not found"}
    return {"data": kalimat}


@examrouter.get("/start/{idmateriujian}")
def start_ujian(
    idmateriujian: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    # Ambil kategori dari tabel Materiujian
    materi = db.query(Materiujian).filter(Materiujian.idmateriujian == idmateriujian).first()
    if not materi:
        return {"error": "Materi tidak ditemukan"}

    # Cek apakah entri ujianfonem sudah ada untuk user dan ujian ini
    ujian_entry = db.query(Ujianfonem).filter(
        Ujianfonem.idtalent == idtalent,
        Ujianfonem.idmateriujian == idmateriujian,
        Ujianfonem.nilai == None
    ).first()

    if not ujian_entry:
        # Buat entri baru ujianfonem jika belum ada
        ujian_entry = Ujianfonem(
            idmateriujian=idmateriujian,
            idtalent=idtalent,
            kategori=materi.kategori,
            nilai=None,
            waktuujian=datetime.utcnow()
        )
        db.add(ujian_entry)
        db.commit()
        db.refresh(ujian_entry)

    id_ujianfonem = ujian_entry.idujian

    # Ambil semua idsoal yang sudah dikerjakan dari detailujianfonem
    existing_details = db.query(Detailujianfonem.idsoal).filter(
        Detailujianfonem.idujian == id_ujianfonem
    ).all()
    sudah_dikerjakan_ids = {detail.idsoal for detail in existing_details}

    # Hitung berapa yang sudah dikerjakan
    if len(sudah_dikerjakan_ids) >= 10:
        return {
            "message": "Ujian telah selesai",
            "id_ujianfonem": id_ujianfonem,
            "data": []  # tidak perlu tampilkan soal lagi
        }

    # Ambil sisa kalimat yang belum dikerjakan
    sisa_kalimat_objs = db.query(Materiujiankalimat).filter(
        Materiujiankalimat.idmateriujian == idmateriujian,
        ~Materiujiankalimat.idmateriujiankalimat.in_(sudah_dikerjakan_ids)
    ).all()

    sisa_kalimat = [
        {
            "id": k.idmateriujiankalimat,
            "kalimat": k.kalimat,
            "fonem": k.fonem
        }
        for k in sisa_kalimat_objs
    ]

    return {
        "id_ujianfonem": id_ujianfonem,
        "remaining": len(sisa_kalimat),
        "data": sisa_kalimat
    }


@examrouter.post("/compare")
async def compare_phonemes_with_ujian(
    idContent: int = Form(...),       # idmaterifonemkalimat
    idUjian: int = Form(...),         # idujianfonem
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Membandingkan fonem kalimat ujian menggunakan sistem analisis yang sama dengan PhonemeRecognitionView
    """
    try:
        # Authentication
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Validasi konten kalimat ujian
        content = db.query(Materiujiankalimat).filter(
            Materiujiankalimat.idmateriujiankalimat == idContent
        ).first()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        # Validasi ujian
        ujian = db.query(Ujianfonem).filter(
            Ujianfonem.idujian == idUjian,
            Ujianfonem.idtalent == idtalent
        ).first()
        if not ujian:
            raise HTTPException(status_code=404, detail="Ujian not found for this user")

        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Process audio and analyze pronunciation
        audio_data = await file.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        # Gunakan analyze_pronunciation yang sama dengan PhonemeRecognitionView
        analysis_result = await analyze_pronunciation(
            audio_data=audio_data,
            id_content=idContent,
            db=db,
            content_type="exam"
        )
        
        if "error" in analysis_result:
            logger.error(f"Pronunciation analysis error: {analysis_result['error']}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {analysis_result['error']}")
        
        # Extract analysis data
        target_phonemes = analysis_result["target_phonemes"]
        user_phonemes = analysis_result["user_phonemes"]
        gemini_analysis = analysis_result["analysis"]
        
        # Create enhanced alignment with status classification (sama dengan PhonemeRecognitionView)
        alignment = create_enhanced_alignment(target_phonemes, user_phonemes, gemini_analysis)
        
        # Calculate enhanced accuracy (sama dengan PhonemeRecognitionView)
        accuracy_score = calculate_enhanced_accuracy(alignment)
        
        # Simpan ke detailujianfonem
        detail = Detailujianfonem(
            idujian=idUjian,
            idsoal=idContent,
            nilai=accuracy_score
        )
        db.add(detail)
        db.commit()

        logger.info(f"Exam phoneme comparison completed for user {idtalent}, content {idContent}")

        # Format response menggunakan helper yang sama dengan PhonemeRecognitionView
        response = format_enhanced_phoneme_response(
            alignment, gemini_analysis, target_phonemes, user_phonemes
        )
        
        # Tambahkan informasi spesifik untuk exam
        response.update({
            "success": True,
            "exam_info": {
                "idUjian": idUjian,
                "idContent": idContent,
                "accuracy_score": accuracy_score
            }
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_phonemes_with_ujian: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@examrouter.post("/compare_simple")
async def compare_phonemes_simple(
    idContent: int = Form(...),       # idmaterifonemkalimat
    idUjian: int = Form(...),         # idujianfonem
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Versi sederhana untuk backward compatibility - hanya mengembalikan skor
    """
    try:
        # Ambil ID Talent dari token
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Validasi konten kalimat
        content = db.query(Materiujiankalimat).filter(Materiujiankalimat.idmateriujiankalimat == idContent).first()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        # Validasi ujian
        ujian = db.query(Ujianfonem).filter(
            Ujianfonem.idujian == idUjian,
            Ujianfonem.idtalent == idtalent
        ).first()
        if not ujian:
            raise HTTPException(status_code=404, detail="Ujian not found for this user")

        # Proses audio sederhana
        audio_data = await file.read()
        audio = audio_processor.preprocess_audio(audio_data)
        user_phonemes = audio_processor.infer_phonemes(audio)
        
        # Dapatkan target phonemes dari kalimat
        target_phonemes = text_to_ipa_gruut(content.kalimat)
        
        # Hitung similarity sederhana berdasarkan panjang dan kesamaan
        target_list = target_phonemes.split()
        user_list = user_phonemes.split()
        
        # Simple similarity calculation
        if len(target_list) == 0:
            similarity = 0
        else:
            # Hitung berapa phoneme yang cocok
            matches = 0
            min_length = min(len(target_list), len(user_list))
            for i in range(min_length):
                if i < len(target_list) and i < len(user_list):
                    if target_list[i] == user_list[i]:
                        matches += 1
            
            # Penalti untuk perbedaan panjang
            length_penalty = abs(len(target_list) - len(user_list)) * 0.1
            similarity = max(0, (matches / len(target_list)) * 100 - length_penalty)
        
        nilai_persen = round(similarity, 2)

        # Simpan ke detailujianfonem
        detail = Detailujianfonem(
            idujian=idUjian,
            idsoal=idContent,
            nilai=nilai_persen
        )
        db.add(detail)
        db.commit()

        # Return hasil sederhana
        return {
            "success": True,
            "similarity_percent": f"{nilai_persen}%",
            "target_phonemes": target_phonemes,
            "user_phonemes": user_phonemes,
            "method": "simple_comparison"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_phonemes_simple: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@examrouter.get("/result/{idujian}")
def get_ujian_result(
    idujian: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    # Ambil entri ujianfonem
    ujian = db.query(Ujianfonem).filter(
        Ujianfonem.idujian == idujian,
        Ujianfonem.idtalent == idtalent
    ).first()

    if not ujian:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")

    # Ambil semua detail jawaban ujian
    details = db.query(Detailujianfonem).filter(
        Detailujianfonem.idujian == idujian
    ).all()

    if not details:
        raise HTTPException(status_code=400, detail="Belum ada jawaban dalam detail ujian")

    # Hitung nilai rata-rata
    total_nilai = sum([d.nilai for d in details if d.nilai is not None])
    jumlah = len(details)
    rata_rata = round(total_nilai / jumlah, 2)

    # Update nilai rata-rata ke tabel ujian
    ujian.nilai = rata_rata
    db.commit()

    # Ambil daftar soal untuk menampilkan kalimat
    soal_ids = [d.idsoal for d in details]
    soal_map = {
        s.idmateriujiankalimat: s.kalimat
        for s in db.query(Materiujiankalimat).filter(Materiujiankalimat.idmateriujiankalimat.in_(soal_ids)).all()
    }

    # Siapkan response
    return {
        "success": True,
        "id_ujian": ujian.idujian,
        "kategori": ujian.kategori,
        "jumlah_soal": jumlah,
        "nilai_rata_rata": rata_rata,
        "detail": [
            {
                "idsoal": d.idsoal,
                "kalimat": soal_map.get(d.idsoal, "-"),
                "nilai": d.nilai
            }
            for d in details
        ]
    }


@examrouter.get("/analysis/{idujian}")
def get_detailed_analysis(
    idujian: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """
    Endpoint baru untuk mendapatkan analisis detail jika diperlukan
    """
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    # Ambil entri ujianfonem
    ujian = db.query(Ujianfonem).filter(
        Ujianfonem.idujian == idujian,
        Ujianfonem.idtalent == idtalent
    ).first()

    if not ujian:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")

    # Ambil semua detail jawaban ujian
    details = db.query(Detailujianfonem).filter(
        Detailujianfonem.idujian == idujian
    ).all()

    if not details:
        raise HTTPException(status_code=400, detail="Belum ada jawaban dalam detail ujian")

    # Analisis per kategori phoneme jika diperlukan
    kategori_analysis = {
        "vowels": [],
        "consonants": [],
        "diphthongs": []
    }

    return {
        "success": True,
        "id_ujian": ujian.idujian,
        "kategori": ujian.kategori,
        "total_questions": len(details),
        "average_score": ujian.nilai,
        "category_analysis": kategori_analysis,
        "recommendations": [
            "Practice phoneme recognition daily",
            "Focus on problematic sounds",
            "Record yourself speaking"
        ]
    }


# Tambahkan endpoint ini ke ExamView.py

@examrouter.delete("/delete/{idujian}")
def delete_ujian_fonem(
    idujian: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """
    Menghapus ujian fonem beserta semua detail ujiannya
    """
    try:
        # Validasi user authentication
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Cek apakah ujian fonem exists dan milik user yang benar
        ujian = db.query(Ujianfonem).filter(
            Ujianfonem.idujian == idujian,
            Ujianfonem.idtalent == idtalent
        ).first()

        if not ujian:
            raise HTTPException(
                status_code=404, 
                detail="Ujian fonem tidak ditemukan atau bukan milik user ini"
            )

        # Hapus semua detail ujian fonem terlebih dahulu (foreign key constraint)
        detail_count = db.query(Detailujianfonem).filter(
            Detailujianfonem.idujian == idujian
        ).count()

        db.query(Detailujianfonem).filter(
            Detailujianfonem.idujian == idujian
        ).delete()

        # Hapus ujian fonem
        db.query(Ujianfonem).filter(
            Ujianfonem.idujian == idujian,
            Ujianfonem.idtalent == idtalent
        ).delete()

        # Commit perubahan
        db.commit()

        return {
            "success": True,
            "message": "Ujian fonem berhasil dihapus",
            "deleted_exam": {
                "idujian": idujian,
                "kategori": ujian.kategori,
                "deleted_details_count": detail_count
            }
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting ujian fonem {idujian}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Gagal menghapus ujian fonem: {str(e)}"
        )


@examrouter.delete("/delete-details/{idujian}")
def delete_ujian_details_only(
    idujian: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """
    Menghapus hanya detail ujian fonem (untuk reset ujian), 
    ujian fonem tetap ada tapi nilai direset ke None
    """
    try:
        # Validasi user authentication
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Cek apakah ujian fonem exists dan milik user yang benar
        ujian = db.query(Ujianfonem).filter(
            Ujianfonem.idujian == idujian,
            Ujianfonem.idtalent == idtalent
        ).first()

        if not ujian:
            raise HTTPException(
                status_code=404, 
                detail="Ujian fonem tidak ditemukan atau bukan milik user ini"
            )

        # Hapus semua detail ujian fonem
        detail_count = db.query(Detailujianfonem).filter(
            Detailujianfonem.idujian == idujian
        ).count()

        db.query(Detailujianfonem).filter(
            Detailujianfonem.idujian == idujian
        ).delete()

        # Reset nilai ujian ke None
        ujian.nilai = None
        ujian.waktuujian = datetime.utcnow()  # Update waktu ujian

        # Commit perubahan
        db.commit()

        return {
            "success": True,
            "message": "Detail ujian fonem berhasil dihapus, ujian direset",
            "reset_exam": {
                "idujian": idujian,
                "kategori": ujian.kategori,
                "deleted_details_count": detail_count,
                "status": "ready_for_retake"
            }
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting ujian details {idujian}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Gagal menghapus detail ujian: {str(e)}"
        )