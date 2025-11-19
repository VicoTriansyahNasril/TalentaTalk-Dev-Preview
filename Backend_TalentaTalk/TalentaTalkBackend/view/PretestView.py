#PretestView.py
from fastapi import APIRouter, Depends, Header, Form, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Talent
from controller.AuthController import get_current_user
import random
from models import Materifonemkalimat, Materiujian, Materiujiankalimat
from sqlalchemy.sql import func
from controller.PhonemeRecognitionController import (
    audio_processor,
    create_enhanced_alignment,
    calculate_enhanced_accuracy,
    get_alignment_statistics,
    format_enhanced_phoneme_response,
    get_phoneme_status, is_phoneme_similar, analyze_pronunciation
)
from schemas import PretestScoreRequest
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

pretestrouter = APIRouter(prefix="/pretest", tags=["Pretest"])

@pretestrouter.get("/check")
def check_onboarding(authorization: str = Header(None), db: Session = Depends(get_db)):
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]
    talent = db.query(Talent).filter(Talent.idtalent == idtalent).first()
    if talent is None:
        return {"error": "Talent not found"}
    show_onboarding = talent.pretest_score is None
    return {"show_onboarding": show_onboarding}


@pretestrouter.get("/start")
def get_random_kalimat(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    # Validasi user login
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    # Ambil semua kategori unik
    kategori_list = db.query(Materifonemkalimat.kategori).distinct().all()
    kategori_list = [k[0] for k in kategori_list]

    # Acak kategorinya dan ambil 10
    random.shuffle(kategori_list)
    kategori_terpilih = kategori_list[:10]

    # Ambil satu kalimat acak dari masing-masing kategori
    hasil = []
    for kategori in kategori_terpilih:
        kalimat = (
            db.query(Materifonemkalimat)
            .filter(Materifonemkalimat.kategori == kategori)
            .order_by(func.random())
            .limit(1)
            .first()
        )
        if kalimat:
            hasil.append({
                "id": kalimat.idmaterifonemkalimat,
                "kategori": kalimat.kategori,
                "kalimat": kalimat.kalimat,
                "fonem": kalimat.fonem
            })

    return {"data": hasil}

# @pretestrouter.get("/start")
# def get_random_kalimat(
#     authorization: str = Header(None),
#     db: Session = Depends(get_db)
# ):
#     # Validasi user login
#     current_user = get_current_user(authorization)
#     idtalent = current_user["idtalent"]

#     # Ambil semua kategori unik dari materiujian
#     kategori_list = db.query(Materiujian.kategori).distinct().all()
#     kategori_list = [k[0] for k in kategori_list]

#     # Acak kategorinya dan ambil 10
#     random.shuffle(kategori_list)
#     kategori_terpilih = kategori_list[:10]

#     # Ambil satu kalimat acak dari masing-masing kategori
#     hasil = []
#     for kategori in kategori_terpilih:
#         # Join antara materiujian dan materiujiankalimat untuk mendapatkan kalimat
#         kalimat_data = (
#             db.query(Materiujiankalimat, Materiujian.kategori)
#             .join(Materiujian, Materiujiankalimat.idmateriujian == Materiujian.idmateriujian)
#             .filter(Materiujian.kategori == kategori)
#             .order_by(func.random())
#             .limit(1)
#             .first()
#         )
        
#         if kalimat_data:
#             kalimat, kategori_nama = kalimat_data
#             hasil.append({
#                 "id": kalimat.idmateriujiankalimat,
#                 "kategori": kategori_nama,
#                 "kalimat": kalimat.kalimat,
#                 "fonem": kalimat.fonem
#             })

#     return {"data": hasil}

@pretestrouter.post("/compare")
async def compare_phonemes(
    idContent: int = Form(...),
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:
        # Authentication
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]
        
        # Validate content from database
        content = db.query(Materifonemkalimat).filter(
            Materifonemkalimat.idmaterifonemkalimat == idContent
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Process audio and analyze pronunciation
        audio_data = await file.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        analysis_result = await analyze_pronunciation(
            audio_data=audio_data,
            id_content=idContent,
            db=db,
            content_type="sentence"
        )
        
        if "error" in analysis_result:
            logger.error(f"Pronunciation analysis error: {analysis_result['error']}")
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        target_phonemes = analysis_result["target_phonemes"]
        user_phonemes = analysis_result["user_phonemes"]
        gemini_analysis = analysis_result["analysis"]
        
        alignment = create_enhanced_alignment(target_phonemes, user_phonemes, gemini_analysis)
        
        accuracy_score = calculate_enhanced_accuracy(alignment)
        
        alignment_stats = get_alignment_statistics(alignment)
        
        logger.info(f"Pretest phoneme comparison completed for user {idtalent}, content {idContent}")
        
        return {
            "kalimat_target": content.kalimat,
            "target_phonemes": target_phonemes,
            "user_phonemes": user_phonemes,
            "similarity_percent": f"{accuracy_score}%",
            "accuracy_score": accuracy_score,
            "phoneme_comparison": alignment,
            "gemini_analysis": gemini_analysis,
            "alignment_statistics": alignment_stats,
            "overall_feedback": gemini_analysis.get("overall_feedback", "Analysis completed"),
            "intelligibility_level": gemini_analysis.get("intelligibility_level", "Unknown"),
            "native_understandable": gemini_analysis.get("native_understandable", False),
            "improvement_tips": gemini_analysis.get("improvement_tips", []),
            "specific_issues": gemini_analysis.get("specific_issues", []),
            "strengths": gemini_analysis.get("strengths", []),
            "confidence_level": gemini_analysis.get("confidence_level", "Unknown"),
            "method": "enhanced_gemini_analysis"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in pretest compare_phonemes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@pretestrouter.post("/compare_simple")
async def compare_phonemes_simple(
    idContent: int = Form(...),
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Versi sederhana untuk backward compatibility atau fallback
    Menggunakan analisis phoneme sederhana tanpa AI
    """
    try:
        # Ambil ID user dari token
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Ambil konten target dari DB
        content = db.query(Materifonemkalimat).filter(Materifonemkalimat.idmaterifonemkalimat == idContent).first()
        if not content:
            return {"error": "Content not found"}

        # Target kalimat
        target_sentence = content.kalimat

        # Proses audio sederhana
        audio_data = await file.read()
        audio = audio_processor.preprocess_audio(audio_data)
        user_phonemes = audio_processor.infer_phonemes(audio)
        
        # Dapatkan target phonemes dari kalimat
        target_phonemes = text_to_ipa_gruut(target_sentence)
        
        # Hitung similarity sederhana
        target_list = target_phonemes.split()
        user_list = user_phonemes.split()
        
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

        # Return hasil sederhana
        return {
            "kalimat_target": target_sentence,
            "target_phonemes": target_phonemes,
            "user_phonemes": user_phonemes,
            "similarity_percent": f"{nilai_persen}%",
            "accuracy_score": nilai_persen,
            "phoneme_comparison": [],  # Tidak ada comparison detail untuk versi sederhana
            "overall_feedback": f"Simple analysis completed with {nilai_persen}% accuracy",
            "method": "simple_comparison"
        }
        
    except Exception as e:
        logger.error(f"Error in compare_phonemes_simple: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}


@pretestrouter.post("/compare_basic")
async def compare_phonemes_basic(
    idContent: int = Form(...),
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Versi paling dasar untuk compatibility dengan format response lama
    """
    try:
        # Ambil ID user dari token
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Ambil konten target dari DB
        content = db.query(Materifonemkalimat).filter(Materifonemkalimat.idmaterifonemkalimat == idContent).first()
        if not content:
            return {"error": "Content not found"}

        # Target fonem & kalimat (format lama)
        target_phonemes = list(content.fonem.replace(" ", ""))
        target_sentence = content.kalimat

        # Proses audio
        audio_data = await file.read()
        audio = audio_processor.preprocess_audio(audio_data)
        user_phonemes = audio_processor.infer_phonemes(audio).split()

        # Hitung similarity basic
        if len(target_phonemes) == 0:
            similarity = 0
        else:
            matches = 0
            min_length = min(len(target_phonemes), len(user_phonemes))
            for i in range(min_length):
                if i < len(target_phonemes) and i < len(user_phonemes):
                    if target_phonemes[i] == user_phonemes[i]:
                        matches += 1
            
            similarity = (matches / len(target_phonemes)) * 100
        
        nilai_persen = round(similarity, 2)

        # Return hasil format lama
        return {
            "kalimat_target": target_sentence,
            "target_phonemes": target_phonemes,
            "user_phonemes": user_phonemes,
            "similarity_percent": f"{nilai_persen}%",
            "phoneme_comparison": [],  # Empty untuk compatibility
        }
        
    except Exception as e:
        logger.error(f"Error in compare_phonemes_basic: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}


@pretestrouter.post("/submit")
def submit_pretest_score(
    request: PretestScoreRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    # Ambil ID user dari JWT
    current_user = get_current_user(authorization)
    idtalent = current_user["idtalent"]

    # Cek apakah user ada
    talent = db.query(Talent).filter(Talent.idtalent == idtalent).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    # Update nilai pretest
    talent.pretest_score = request.score
    db.commit()

    return {"message": "Pretest score saved successfully", "score": talent.pretest_score}


@pretestrouter.get("/progress/{idtalent}")
def get_pretest_progress(
    idtalent: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint baru untuk mendapatkan progress pretest user
    """
    current_user = get_current_user(authorization)
    
    # Cek apakah user berhak mengakses data ini
    if current_user["idtalent"] != idtalent:
        raise HTTPException(status_code=403, detail="Access denied")
    
    talent = db.query(Talent).filter(Talent.idtalent == idtalent).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    return {
        "idtalent": idtalent,
        "pretest_completed": talent.pretest_score is not None,
        "pretest_score": talent.pretest_score,
        "onboarding_required": talent.pretest_score is None
    }


@pretestrouter.get("/statistics")
def get_pretest_statistics(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk mendapatkan statistik pretest secara umum
    """
    current_user = get_current_user(authorization)
    
    # Hitung statistik basic
    total_users = db.query(Talent).count()
    completed_pretest = db.query(Talent).filter(Talent.pretest_score.isnot(None)).count()
    
    if completed_pretest > 0:
        avg_score = db.query(func.avg(Talent.pretest_score)).filter(Talent.pretest_score.isnot(None)).scalar()
        avg_score = round(avg_score, 2) if avg_score else 0
    else:
        avg_score = 0
    
    return {
        "total_users": total_users,
        "completed_pretest": completed_pretest,
        "completion_rate": round((completed_pretest / total_users) * 100, 2) if total_users > 0 else 0,
        "average_score": avg_score
    }