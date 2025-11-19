# PhonemeRecognitionView.py
from fastapi import APIRouter, UploadFile, File, Form, Query, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
import random
import logging
from controller.PhonemeRecognitionController import (
    audio_processor, text_to_ipa_gruut, analyze_pronunciation
)
from controller.AuthController import get_current_user
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import Materifonemkalimat, Materifonemkata, Hasillatihanfonem
from datetime import datetime
from sqlalchemy.sql.expression import func
from difflib import SequenceMatcher

# Setup logging
logger = logging.getLogger(__name__)

phonemerecognitionrouter = APIRouter(prefix="/phoneme", tags=["Phoneme Recognition"])

# Enhanced phoneme similarity mapping
SIMILAR_PHONEMES = {
    # Vowel Pairs
    "i": ["ɪ"],
    "ɪ": ["i", "ɛ"],
    "ɛ": ["æ", "ɪ"],
    "æ": ["ɛ"],
    "ə": ["ʌ", "ɚ"],
    "ɚ": ["ə", "ʌ"],
    "ʌ": ["ə", "ɚ"],
    "ɑ": ["ɔ", "ʌ"],
    "ɔ": ["oʊ", "ɑ"],
    "oʊ": ["ɔ", "ʊ"],
    "ʊ": ["u", "oʊ"],
    "u": ["ʊ"],
    # Diphthong Pairs (based on ending/starting vowels)
    "eɪ": ["ɛ", "ɪ"],
    "aɪ": ["ɪ", "ɑ"],
    "ɔɪ": ["ɔ", "ɪ"],
    "aʊ": ["ʊ", "ɑ"],
    # Voiced/Voiceless Consonant Pairs
    "p": ["b"],
    "b": ["p"],
    "t": ["d"],
    "d": ["t"],
    "k": ["g"],
    "g": ["k"],
    "f": ["v"],
    "v": ["f"],
    "θ": ["ð"],
    "ð": ["θ"],
    "s": ["z"],
    "z": ["s"],
    "ʃ": ["ʒ"],
    "ʒ": ["ʃ"],
    "tʃ": ["dʒ"],
    "dʒ": ["tʃ"],
    "m": ["n"],
    "n": ["m", "ŋ"],
    "ŋ": ["n"],
    "l": ["r"],
    "r": ["l"],
    "j": ["i"],
    "w": ["u"],
}

def is_phoneme_similar(target_phoneme: str, user_phoneme: str) -> bool:
    """Check if two phonemes are phonetically similar"""
    if target_phoneme == user_phoneme:
        return True
    
    # Check if user phoneme is in the similar list for target phoneme
    similar_list = SIMILAR_PHONEMES.get(target_phoneme, [])
    return user_phoneme in similar_list

def get_phoneme_status(target_phoneme: str, user_phoneme: str) -> tuple[str, int]:
    """
    Determine the status and similarity score for phoneme comparison
    Returns: (status, similarity_score)
    """
    if not target_phoneme and not user_phoneme:
        return "correct", 100
    
    if not target_phoneme and user_phoneme:
        return "extra", 0
    
    if target_phoneme and not user_phoneme:
        return "missing", 0
    
    if target_phoneme == user_phoneme:
        return "correct", 100
    
    if is_phoneme_similar(target_phoneme, user_phoneme):
        return "similar", 75
    
    return "incorrect", 0


def create_enhanced_alignment_with_sequence_matcher(target_phonemes: str, user_phonemes: str) -> List[Dict]:
    """Create alignment using SequenceMatcher as fallback"""
    target_list = target_phonemes.split()
    user_list = user_phonemes.split()
    
    # Use SequenceMatcher for alignment
    matcher = SequenceMatcher(None, target_list, user_list)
    alignment = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Exact matches
            for k in range(i2 - i1):
                target_phoneme = target_list[i1 + k]
                user_phoneme = user_list[j1 + k]
                status, similarity_score = get_phoneme_status(target_phoneme, user_phoneme)
                
                alignment.append({
                    "target": target_phoneme,
                    "user": user_phoneme,
                    "status": status,
                    "match_type": "match",
                    "similarity": similarity_score
                })
        
        elif tag == 'replace':
            # Handle substitutions
            target_phonemes_segment = target_list[i1:i2]
            user_phonemes_segment = user_list[j1:j2]
            
            # Align segments of different lengths
            max_len = max(len(target_phonemes_segment), len(user_phonemes_segment))
            
            for k in range(max_len):
                target_phoneme = target_phonemes_segment[k] if k < len(target_phonemes_segment) else ""
                user_phoneme = user_phonemes_segment[k] if k < len(user_phonemes_segment) else ""
                
                status, similarity_score = get_phoneme_status(target_phoneme, user_phoneme)
                
                # Determine match_type based on status
                if status == "correct":
                    match_type = "match"
                elif status == "similar":
                    match_type = "similar"
                elif status == "missing":
                    match_type = "delete"
                elif status == "extra":
                    match_type = "insert"
                else:
                    match_type = "replace"
                
                alignment.append({
                    "target": target_phoneme,
                    "user": user_phoneme,
                    "status": status,
                    "match_type": match_type,
                    "similarity": similarity_score
                })
        
        elif tag == 'delete':
            # Missing phonemes (in target but not in user)
            for k in range(i2 - i1):
                target_phoneme = target_list[i1 + k]
                status, similarity_score = get_phoneme_status(target_phoneme, "")
                
                alignment.append({
                    "target": target_phoneme,
                    "user": "",
                    "status": status,
                    "match_type": "delete",
                    "similarity": similarity_score
                })
        
        elif tag == 'insert':
            # Extra phonemes (in user but not in target)
            for k in range(j2 - j1):
                user_phoneme = user_list[j1 + k]
                status, similarity_score = get_phoneme_status("", user_phoneme)
                
                alignment.append({
                    "target": "",
                    "user": user_phoneme,
                    "status": status,
                    "match_type": "insert",
                    "similarity": similarity_score
                })
    
    return alignment


def create_enhanced_alignment(target_phonemes: str, user_phonemes: str, gemini_analysis: Dict) -> List[Dict]:
    """Create enhanced alignment with detailed status classification"""
    target_list = target_phonemes.split()
    user_list = user_phonemes.split()
    
    # If Gemini provides detailed phoneme comparison, enhance it with our status system
    if "phoneme_comparison" in gemini_analysis and gemini_analysis["phoneme_comparison"]:
        alignment = []
        for comparison in gemini_analysis["phoneme_comparison"]:
            target_phoneme = comparison.get("target", "")
            user_phoneme = comparison.get("user", "")
            
            # Get enhanced status and similarity
            status, similarity_score = get_phoneme_status(target_phoneme, user_phoneme)
            
            # Map to legacy match_type for backward compatibility
            if status == "correct":
                match_type = "match"
            elif status == "similar":
                match_type = "similar"
            elif status == "incorrect":
                match_type = "replace"
            elif status == "missing":
                match_type = "delete"
            elif status == "extra":
                match_type = "insert"
            else:
                match_type = "unknown"
            
            alignment.append({
                "target": target_phoneme,
                "user": user_phoneme,
                "status": status,  # New enhanced status
                "match_type": match_type,  # Keep for backward compatibility
                "similarity": similarity_score
            })
        return alignment
    
    # Fallback: Use SequenceMatcher when Gemini analysis is not available or incomplete
    return create_enhanced_alignment_with_sequence_matcher(target_phonemes, user_phonemes)

def calculate_enhanced_accuracy(alignment: List[Dict]) -> float:
    """Calculate accuracy score based on enhanced phoneme comparison"""
    if not alignment:
        return 0.0
    
    total_score = 0
    total_phonemes = len(alignment)
    
    for phoneme_comparison in alignment:
        status = phoneme_comparison.get("status", "incorrect")
        if status == "correct":
            total_score += 100
        elif status == "similar":
            total_score += 75
        elif status == "incorrect":
            total_score += 0
        elif status == "missing":
            total_score += 0
        elif status == "extra":
            total_score += 0  # Extra phonemes don't contribute to score
    
    return round(total_score / total_phonemes, 1) if total_phonemes > 0 else 0.0

def get_alignment_statistics(alignment: List[Dict]) -> Dict:
    """Get detailed statistics from alignment"""
    stats = {
        "total_phonemes_target": 0,
        "total_phonemes_user": 0,
        "correct_phonemes": 0,
        "similar_phonemes": 0,
        "incorrect_phonemes": 0,
        "missing_phonemes": 0,
        "extra_phonemes": 0
    }
    
    for phoneme_comparison in alignment:
        status = phoneme_comparison.get("status", "incorrect")
        target = phoneme_comparison.get("target", "")
        user = phoneme_comparison.get("user", "")
        
        if target:
            stats["total_phonemes_target"] += 1
        if user:
            stats["total_phonemes_user"] += 1
        
        if status == "correct":
            stats["correct_phonemes"] += 1
        elif status == "similar":
            stats["similar_phonemes"] += 1
        elif status == "incorrect":
            stats["incorrect_phonemes"] += 1
        elif status == "missing":
            stats["missing_phonemes"] += 1
        elif status == "extra":
            stats["extra_phonemes"] += 1
    
    return stats

# Helper function untuk error handling
def handle_database_error(error: Exception, operation: str) -> HTTPException:
    """Helper function untuk menangani error database"""
    logger.error(f"Database error during {operation}: {str(error)}")
    raise HTTPException(status_code=500, detail=f"Database error: {operation}")

def handle_audio_processing_error(error: Exception) -> HTTPException:
    """Helper function untuk menangani error audio processing"""
    logger.error(f"Audio processing error: {str(error)}")
    raise HTTPException(status_code=400, detail="Audio processing failed")

def handle_authentication_error(error: Exception) -> HTTPException:
    """Helper function untuk menangani error autentikasi"""
    logger.error(f"Authentication error: {str(error)}")
    raise HTTPException(status_code=401, detail="Authentication failed")

# Enhanced helper function untuk format response
def format_enhanced_phoneme_response(
    alignment: List[Dict],
    gemini_analysis: Dict,
    target_phonemes: str,
    user_phonemes: str
) -> Dict:
    """Enhanced helper function untuk format response phoneme comparison"""
    
    # Calculate enhanced accuracy score
    accuracy_score = calculate_enhanced_accuracy(alignment)
    
    # Get detailed statistics
    alignment_stats = get_alignment_statistics(alignment)
    
    # Update gemini analysis with our enhanced data
    enhanced_gemini_analysis = gemini_analysis.copy()
    enhanced_gemini_analysis["accuracy_score"] = accuracy_score
    enhanced_gemini_analysis["alignment_analysis"] = alignment_stats
    
    return {
        "similarity_percent": f"{accuracy_score}%",
        "phoneme_comparison": alignment,
        "gemini_analysis": enhanced_gemini_analysis,
        "target_phonemes": target_phonemes,
        "user_phonemes": user_phonemes,
        "alignment_statistics": alignment_stats
    }

@phonemerecognitionrouter.post("/compare")
async def compare_phonemes(
    idContent: int = Form(...), 
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Membandingkan fonem dari audio yang diunggah dengan fonem target dari database
    """
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
            
        # analysis_result = await analyze_pronunciation(audio_data, content.kalimat)
        analysis_result = await analyze_pronunciation(
            audio_data=audio_data,
            id_content=idContent,
            db=db,
            content_type="sentence"
        )
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Extract analysis data
        target_phonemes = analysis_result["target_phonemes"]
        user_phonemes = analysis_result["user_phonemes"]
        gemini_analysis = analysis_result["analysis"]
        
        # Create enhanced alignment with status classification
        alignment = create_enhanced_alignment(target_phonemes, user_phonemes, gemini_analysis)
        
        # Calculate enhanced accuracy
        accuracy_score = calculate_enhanced_accuracy(alignment)
        
        # Save to database
        new_result = Hasillatihanfonem(
            typelatihan="Sentence",
            idtalent=idtalent,
            idsoal=idContent,
            nilai=accuracy_score,
            waktulatihan=datetime.now(),
            phoneme_comparison=alignment 
        )
        
        db.add(new_result)
        db.commit()
        
        logger.info(f"Sentence phoneme comparison completed for user {idtalent}, content {idContent}")
        
        return format_enhanced_phoneme_response(
            alignment, gemini_analysis, target_phonemes, user_phonemes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in compare_phonemes: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@phonemerecognitionrouter.post("/compare_word")
async def compare_phonemes_word(
    idContent: int = Form(...),
    authorization: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Membandingkan fonem dari audio yang diunggah dengan fonem target kata dari database.
    """
    try:
        # Authentication
        current_user = get_current_user(authorization)
        idtalent = current_user["idtalent"]

        # Validate content from database
        target_data = db.query(Materifonemkata).filter(
            Materifonemkata.idmaterifonemkata == idContent
        ).first()
        
        if not target_data:
            raise HTTPException(status_code=404, detail="Content not found")

        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Process audio and analyze pronunciation
        audio_data = await file.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        # analysis_result = await analyze_pronunciation(audio_data, target_data.kata)
        analysis_result = await analyze_pronunciation(
            audio_data=audio_data,
            id_content=idContent,
            db=db,
            content_type="word"
        )

        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Extract analysis data
        target_phonemes = analysis_result["target_phonemes"]
        user_phonemes = analysis_result["user_phonemes"]
        gemini_analysis = analysis_result["analysis"]
        
        # Create enhanced alignment with status classification
        alignment = create_enhanced_alignment(target_phonemes, user_phonemes, gemini_analysis)
        
        # Calculate enhanced accuracy
        accuracy_score = calculate_enhanced_accuracy(alignment)

        # Save to database
        new_result = Hasillatihanfonem(
            typelatihan="Word",
            idtalent=idtalent,
            idsoal=idContent,
            nilai=accuracy_score,
            waktulatihan=datetime.now(),
            phoneme_comparison=alignment 
        )
        
        db.add(new_result)
        db.commit()

        logger.info(f"Word phoneme comparison completed for user {idtalent}, content {idContent}")

        return format_enhanced_phoneme_response(
            alignment, gemini_analysis, target_phonemes, user_phonemes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in compare_phonemes_word: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

# Keep all other existing endpoints unchanged...
@phonemerecognitionrouter.get("/phoneme_words_categories")
async def get_phoneme_categories(db: Session = Depends(get_db)):
    """Mendapatkan daftar semua kategori fonem kata yang tersedia dari database"""
    try:
        categories = db.query(Materifonemkata.kategori).distinct().all()
        category_list = [category[0] for category in categories if category[0]]
        
        if not category_list:
            raise HTTPException(status_code=404, detail="No word categories found")
            
        return {"categories": category_list}
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e, "fetching word categories")

@phonemerecognitionrouter.get("/phoneme_sentences_categories")
async def get_phoneme_categories(db: Session = Depends(get_db)):
    """Mendapatkan daftar semua kategori fonem kalimat yang tersedia dari database"""
    try:
        categories = db.query(Materifonemkalimat.kategori).distinct().all()
        category_list = [category[0] for category in categories if category[0]]
        
        if not category_list:
            raise HTTPException(status_code=404, detail="No sentence categories found")
            
        return {"categories": category_list}
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e, "fetching sentence categories")

@phonemerecognitionrouter.get("/sentences_by_category/{category}")
async def list_sentences_by_category(category: str, db: Session = Depends(get_db)):
    """Mendapatkan semua kalimat berdasarkan kategori fonem dari database"""
    try:
        sentences = db.query(Materifonemkalimat).filter(
            Materifonemkalimat.kategori == category
        ).all()
        
        if not sentences:
            raise HTTPException(
                status_code=404, 
                detail=f"No sentences found for category '{category}'"
            )
            
        result = []
        for sentence in sentences:
            result.append({
                "idContent": sentence.idmaterifonemkalimat,
                "content": sentence.kalimat,
                "phoneme": sentence.fonem,
                "phoneme_category": sentence.kategori
            })
            
        return {"category": category, "sentences": result}
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e, f"fetching sentences for category {category}")

@phonemerecognitionrouter.get("/words_by_category/{category}")
async def list_words_by_category(category: str, db: Session = Depends(get_db)):
    """Mendapatkan semua kata berdasarkan kategori fonem dari database"""
    try:
        words = db.query(Materifonemkata).filter(
            Materifonemkata.kategori == category
        ).all()
        
        if not words:
            raise HTTPException(
                status_code=404, 
                detail=f"No words found for category '{category}'"
            )
            
        result = []
        for word in words:
            result.append({
                "idContent": word.idmaterifonemkata,
                "content": word.kata,
                "phoneme": word.fonem,
                "phoneme_category": word.kategori
            })
            
        return {"category": category, "words": result}
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e, f"fetching words for category {category}")

@phonemerecognitionrouter.get("/word_by_id/{id}")
async def word_by_id(id: int, db: Session = Depends(get_db)):
    """Mendapatkan kata berdasarkan id dari database"""
    try:
        word = db.query(Materifonemkata).filter(
            Materifonemkata.idmaterifonemkata == id
        ).first()
        
        if not word:
            raise HTTPException(status_code=404, detail=f"No word found for id '{id}'")
            
        return {
            "idSearch": id,
            "idContent": word.idmaterifonemkata,
            "content": word.kata,
            "meaning": word.meaning,
            "definition": word.definition,
            "phoneme": word.fonem,
            "phoneme_category": word.kategori
        }
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e, f"fetching word by id {id}")

@phonemerecognitionrouter.get("/sentence_by_id/{id}")
async def sentence_by_id(id: int, db: Session = Depends(get_db)):
    """Mendapatkan kalimat berdasarkan id dari database"""
    try:
        sentence = db.query(Materifonemkalimat).filter(
            Materifonemkalimat.idmaterifonemkalimat == id
        ).first()
        
        if not sentence:
            raise HTTPException(status_code=404, detail=f"No sentence found for id '{id}'")
            
        return {
            "idSearch": id,
            "idContent": sentence.idmaterifonemkalimat,
            "content": sentence.kalimat,
            "phoneme": sentence.fonem,
            "phoneme_category": sentence.kategori
        }
        
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error(e, f"fetching sentence by id {id}")

