#PhonemeRecognitionController.py
from typing import List, Dict, Optional, Tuple
from itertools import groupby
import numpy as np
import io
import torch
import librosa
from transformers import AutoProcessor, AutoModelForCTC
from gruut import sentences
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
import logging
import json
from sqlalchemy.orm import Session
from models import Materifonemkalimat, Materifonemkata, Materiujiankalimat, Materiujian, Ujianfonem
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Daftar diftong yang tidak boleh dipisah
DIPHTHONGS = [
    "eɪ", "aɪ", "ɔɪ", "aʊ", "oʊ", "ɪə", "ɛə", "ʊə", "dʒ"
]

# Mapping untuk menormalkan tie bar affricates
TIE_BAR_NORMALIZATION = {
    "d͡ʒ": "dʒ",
    "t͡ʃ": "tʃ",
    "t͡s": "ts",
    "d͡z": "dz"
}


class AudioProcessor:
    def __init__(self, model_checkpoint: str):
        self.model = AutoModelForCTC.from_pretrained(model_checkpoint)
        self.processor = AutoProcessor.from_pretrained(model_checkpoint)
        self.sampling_rate = self.processor.feature_extractor.sampling_rate

    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        return audio / np.max(np.abs(audio))

    def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        audio, _ = librosa.load(io.BytesIO(audio_data), sr=16000)
        return self.normalize_audio(audio)

    def decode_phonemes(self, ids: torch.Tensor, ignore_stress: bool = False) -> str:
        ids = [id_ for id_, _ in groupby(ids)]
        special_token_ids = self.processor.tokenizer.all_special_ids + [self.processor.tokenizer.word_delimiter_token_id]
        phonemes = [self.processor.decode(id_) for id_ in ids if id_ not in special_token_ids]
        prediction = " ".join(phonemes)
        if ignore_stress:
            prediction = prediction.replace("ˈ", "").replace("ˌ", "")
        return prediction

    def infer_phonemes(self, audio: np.ndarray) -> str:
        inputs = self.processor(audio, return_tensors="pt", sampling_rate=self.sampling_rate, padding=True)
        with torch.no_grad():
            logits = self.model(inputs.input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        decoded = self.decode_phonemes(predicted_ids[0], ignore_stress=True)
        deduplicated = remove_duplicate_phonemes_preserve_diphthongs(decoded.split())
        return " ".join(deduplicated)

audio_processor = AudioProcessor("bookbot/wav2vec2-ljspeech-gruut")

def normalize_tie_bar_phonemes(phonemes: List[str]) -> List[str]:
    """Menormalkan fonem dengan tie bar"""
    normalized = []
    for phoneme in phonemes:
        normalized_phoneme = phoneme
        for tie_bar, normal in TIE_BAR_NORMALIZATION.items():
            normalized_phoneme = normalized_phoneme.replace(tie_bar, normal)
        normalized.append(normalized_phoneme)
    return normalized

def reconstruct_diphthongs(phonemes: List[str]) -> List[str]:
    """Menggabungkan kembali fonem yang terpisah menjadi diftong"""
    result = []
    i = 0
    while i < len(phonemes):
        if i < len(phonemes) - 1:
            combined = phonemes[i] + phonemes[i + 1]
            if combined in DIPHTHONGS:
                result.append(combined)
                i += 2
                continue
        result.append(phonemes[i])
        i += 1
    return result

def remove_duplicate_phonemes_preserve_diphthongs(phonemes: List[str]) -> List[str]:
    """Menghapus duplikat fonem dengan mempertahankan diftong"""
    normalized = normalize_tie_bar_phonemes(phonemes)
    reconstructed = reconstruct_diphthongs(normalized)
    
    result = []
    prev_phoneme = None
    for phoneme in reconstructed:
        if phoneme != prev_phoneme:
            result.append(phoneme)
            prev_phoneme = phoneme
    return result

def preprocess_phoneme_sequence(phonemes: List[str]) -> List[str]:
    """Preprocess urutan fonem untuk memastikan diftong tidak terpisah"""
    normalized = normalize_tie_bar_phonemes(phonemes)
    return reconstruct_diphthongs(normalized)

# async def analyze_phonemes_with_gemini(target_phonemes: str, user_phonemes: str, original_text: str) -> Dict[str, any]:
#     """Analyze phoneme accuracy using Gemini API - PURE GEMINI ANALYSIS"""
#     try:
#         gemini_api_key = os.getenv("GEMINI_API_KEY")
#         if not gemini_api_key:
#             logger.error("GEMINI_API_KEY not found in environment variables")
#             return {"error": "GEMINI_API_KEY not found"}
        
#         # Construct detailed prompt for comprehensive phoneme analysis
#         prompt = f"""
#         You are an expert phonetician and pronunciation coach. Analyze the phoneme accuracy between target and user pronunciation.

#         ORIGINAL TEXT: "{original_text}"
#         TARGET PHONEMES (correct): {target_phonemes}
#         USER PHONEMES (actual): {user_phonemes}

#         Provide a comprehensive analysis in this EXACT JSON format:
#         {{
#             "accuracy_score": <number 0-100>,
#             "native_understandable": <true/false>,
#             "overall_feedback": "<brief assessment>",
#             "phoneme_comparison": [
#                 {{
#                     "position": <position number>,
#                     "target": "<target phoneme>",
#                     "user": "<user phoneme>",
#                     "status": "<correct/similar/incorrect/missing/extra>",
#                     "similarity_score": <0-100>,
#                     "feedback": "<specific feedback>"
#                 }}
#             ],
#             "specific_issues": [
#                 {{
#                     "phoneme": "<problematic phoneme>",
#                     "issue": "<description>",
#                     "suggestion": "<improvement tip>"
#                 }}
#             ],
#             "strengths": ["<correctly pronounced phonemes/aspects>"],
#             "improvement_tips": ["<practical pronunciation tips>"],
#             "intelligibility_level": "<Native/Near-Native/Intermediate/Beginner>",
#             "confidence_level": "<High/Medium/Low>",
#             "alignment_analysis": {{
#                 "total_phonemes_target": <number>,
#                 "total_phonemes_user": <number>,
#                 "correct_phonemes": <number>,
#                 "similar_phonemes": <number>,
#                 "incorrect_phonemes": <number>,
#                 "missing_phonemes": <number>,
#                 "extra_phonemes": <number>
#             }}
#         }}

#         ANALYSIS INSTRUCTIONS:
#         1. Compare phonemes position by position
#         2. Handle alignment automatically (insertions, deletions, substitutions)
#         3. Consider phonetic similarity (voiced/voiceless pairs, vowel variations)
#         4. Focus on intelligibility impact
#         5. Provide constructive feedback
#         6. Be accurate but encouraging

#         PHONETIC SIMILARITY GUIDELINES:
#         - Voiced/voiceless: p/b, t/d, k/g, f/v, s/z, ʃ/ʒ, θ/ð
#         - Vowel variations: i/ɪ, ɛ/æ, ʌ/ə, ɔ/ɑ, u/ʊ
#         - Liquids: ɹ/r, l variations
#         - Nasals: m/n, n/ŋ
#         - Diphthongs: eɪ, aɪ, ɔɪ, aʊ, oʊ

#         Return ONLY the JSON response, no additional text.
#         """
        
#         url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
        
#         payload = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": prompt
#                         }
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.1,  # Very low for consistent analysis
#                 "topK": 1,
#                 "topP": 1,
#                 "maxOutputTokens": 4096,
#                 "stopSequences": []
#             }
#         }
        
#         timeout = aiohttp.ClientTimeout(total=45)
#         async with aiohttp.ClientSession(timeout=timeout) as session:
#             async with session.post(url, json=payload) as response:
#                 if response.status != 200:
#                     error_text = await response.text()
#                     logger.error(f"Gemini API error {response.status}: {error_text}")
#                     return {"error": f"Gemini API error: {error_text}"}
                
#                 data = await response.json()
                
#                 if "candidates" in data and len(data["candidates"]) > 0:
#                     candidate = data["candidates"][0]
#                     if "content" in candidate and "parts" in candidate["content"]:
#                         content = candidate["content"]["parts"][0]["text"]
                        
#                         # Parse JSON response
#                         try:
#                             # Clean and extract JSON
#                             content = content.strip()
#                             if content.startswith("json"):
#                                 content = content[7:-3]
#                             elif content.startswith(""):
#                                 content = content[3:-3]
                            
#                             # Find JSON boundaries
#                             json_start = content.find('{')
#                             json_end = content.rfind('}') + 1
#                             if json_start != -1 and json_end != -1:
#                                 json_str = content[json_start:json_end]
#                                 analysis = json.loads(json_str)
#                                 logger.info("Gemini analysis completed successfully")
#                                 return analysis
#                             else:
#                                 logger.error("No valid JSON found in Gemini response")
#                                 return {"error": "Invalid JSON format in response"}
                                
#                         except json.JSONDecodeError as e:
#                             logger.error(f"JSON parsing error: {e}")
#                             logger.error(f"Response content: {content}")
#                             return {"error": f"JSON parsing failed: {str(e)}"}
#                     else:
#                         logger.error("Unexpected response structure")
#                         return {"error": "Unexpected response structure"}
#                 else:
#                     logger.error("No candidates in response")
#                     return {"error": "No analysis candidates"}
                    
#     except asyncio.TimeoutError:
#         logger.error("Request timeout")
#         return {"error": "Request timeout"}
#     except Exception as e:
#         logger.error(f"Request error: {str(e)}")
#         return {"error": f"Request error: {str(e)}"}

async def analyze_phonemes_with_gemini(target_phonemes: str, user_phonemes: str, original_text: str) -> Dict[str, any]:
    """Analyze phoneme accuracy using Gemini API - PURE GEMINI ANALYSIS"""
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return {"error": "GEMINI_API_KEY not found"}
        
        # Handle empty user phonemes case
        if not user_phonemes or user_phonemes.strip() == "":
            user_phonemes_display = "[SILENT/NO AUDIO DETECTED]"
            user_phonemes_for_analysis = ""
        else:
            user_phonemes_display = user_phonemes
            user_phonemes_for_analysis = user_phonemes
        
        # Construct detailed prompt for comprehensive phoneme analysis
        prompt = f"""
        You are an expert phonetician and pronunciation coach. Analyze the phoneme accuracy between target and user pronunciation.

        ORIGINAL TEXT: "{original_text}"
        TARGET PHONEMES (correct): {target_phonemes}
        USER PHONEMES (actual): {user_phonemes_display}

        CRITICAL ANALYSIS RULES:
        1. If USER PHONEMES is "[SILENT/NO AUDIO DETECTED]" or empty, this means NO SOUND was produced
        2. In this case, ALL target phonemes should be marked as "missing" with 0% accuracy
        3. Do NOT assume the user pronounced anything correctly if no audio was detected
        4. Empty user phonemes = 0% accuracy score, all phonemes marked as "missing"

        Provide a comprehensive analysis in this EXACT JSON format:
        {{
            "accuracy_score": <number 0-100>,
            "native_understandable": <true/false>,
            "overall_feedback": "<brief assessment>",
            "phoneme_comparison": [
                {{
                    "position": <position number>,
                    "target": "<target phoneme>",
                    "user": "<user phoneme or empty string>",
                    "status": "<correct/similar/incorrect/missing/extra>",
                    "similarity_score": <0-100>,
                    "feedback": "<specific feedback>"
                }}
            ],
            "specific_issues": [
                {{
                    "phoneme": "<problematic phoneme>",
                    "issue": "<description>",
                    "suggestion": "<improvement tip>"
                }}
            ],
            "strengths": ["<correctly pronounced phonemes/aspects>"],
            "improvement_tips": ["<practical pronunciation tips>"],
            "intelligibility_level": "<Native/Near-Native/Intermediate/Beginner>",
            "confidence_level": "<High/Medium/Low>",
            "alignment_analysis": {{
                "total_phonemes_target": <number>,
                "total_phonemes_user": <number>,
                "correct_phonemes": <number>,
                "similar_phonemes": <number>,
                "incorrect_phonemes": <number>,
                "missing_phonemes": <number>,
                "extra_phonemes": <number>
            }}
        }}

        ANALYSIS INSTRUCTIONS:
        1. IF USER PHONEMES IS EMPTY/SILENT:
           - Set accuracy_score to 0
           - Mark ALL target phonemes as "missing" in phoneme_comparison
           - Set user field to empty string "" for all comparisons
           - Set missing_phonemes count to total_phonemes_target
           - Set all other counts (correct, similar, incorrect, extra) to 0
           - Set native_understandable to false
           - Provide feedback about no audio detected

        2. IF USER PHONEMES ARE PROVIDED:
           - Compare phonemes position by position
           - Handle alignment automatically (insertions, deletions, substitutions)
           - Consider phonetic similarity (voiced/voiceless pairs, vowel variations)
           - Focus on intelligibility impact
           - Provide constructive feedback
           - Be accurate but encouraging

        PHONETIC SIMILARITY GUIDELINES (only when user phonemes exist):
        - Voiced/voiceless: p/b, t/d, k/g, f/v, s/z, ʃ/ʒ, θ/ð
        - Vowel variations: i/ɪ, ɛ/æ, ʌ/ə, ɔ/ɑ, u/ʊ
        - Liquids: ɹ/r, l variations
        - Nasals: m/n, n/ŋ
        - Diphthongs: eɪ, aɪ, ɔɪ, aʊ, oʊ

        Return ONLY the JSON response, no additional text.
        """
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,  # Very low for consistent analysis
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 4096,
                "stopSequences": []
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=45)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Gemini API error {response.status}: {error_text}")
                    return {"error": f"Gemini API error: {error_text}"}
                
                data = await response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        content = candidate["content"]["parts"][0]["text"]
                        
                        # Parse JSON response
                        try:
                            # Clean and extract JSON
                            content = content.strip()
                            if content.startswith("json"):
                                content = content[7:-3]
                            elif content.startswith("```"):
                                content = content[3:-3]
                            
                            # Find JSON boundaries
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            if json_start != -1 and json_end != -1:
                                json_str = content[json_start:json_end]
                                analysis = json.loads(json_str)
                                logger.info("Gemini analysis completed successfully")
                                return analysis
                            else:
                                logger.error("No valid JSON found in Gemini response")
                                return {"error": "Invalid JSON format in response"}
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON parsing error: {e}")
                            logger.error(f"Response content: {content}")
                            return {"error": f"JSON parsing failed: {str(e)}"}
                    else:
                        logger.error("Unexpected response structure")
                        return {"error": "Unexpected response structure"}
                else:
                    logger.error("No candidates in response")
                    return {"error": "No analysis candidates"}
                    
    except asyncio.TimeoutError:
        logger.error("Request timeout")
        return {"error": "Request timeout"}
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return {"error": f"Request error: {str(e)}"}

# def create_simple_fallback_analysis(target_phonemes: str, user_phonemes: str) -> Dict[str, any]:
#     """Simple fallback when Gemini fails - NO SEQUENCE MATCHER"""
#     target_list = target_phonemes.split()
#     user_list = user_phonemes.split()
    
#     # Very simple analysis without complex alignment
#     total_target = len(target_list)
#     total_user = len(user_list)
    
#     # Simple scoring based on length difference
#     length_diff = abs(total_target - total_user)
#     base_score = max(0, 100 - (length_diff * 10))
    
#     return {
#         "accuracy_score": base_score,
#         "native_understandable": base_score >= 70,
#         "overall_feedback": f"Basic analysis: {base_score}% accuracy estimate",
#         "phoneme_comparison": [],
#         "specific_issues": [
#             {
#                 "phoneme": "general",
#                 "issue": "Detailed analysis unavailable",
#                 "suggestion": "Continue practicing pronunciation"
#             }
#         ],
#         "strengths": ["Pronunciation attempt recorded"],
#         "improvement_tips": ["Practice with native speakers", "Record yourself regularly"],
#         "intelligibility_level": "Intermediate" if base_score >= 70 else "Beginner",
#         "confidence_level": "Low",
#         "alignment_analysis": {
#             "total_phonemes_target": total_target,
#             "total_phonemes_user": total_user,
#             "correct_phonemes": 0,
#             "similar_phonemes": 0,
#             "incorrect_phonemes": 0,
#             "missing_phonemes": max(0, total_target - total_user),
#             "extra_phonemes": max(0, total_user - total_target)
#         },
#         "method": "simple_fallback"
#     }

def create_simple_fallback_analysis(target_phonemes: str, user_phonemes: str) -> Dict[str, any]:
    """Simple fallback when Gemini fails - handles empty user phonemes correctly"""
    target_list = target_phonemes.split()
    user_list = user_phonemes.split() if user_phonemes and user_phonemes.strip() else []
    
    total_target = len(target_list)
    total_user = len(user_list)
    
    # Handle empty user phonemes case
    if total_user == 0:
        return {
            "accuracy_score": 0,
            "native_understandable": False,
            "overall_feedback": "No audio detected - please try recording again",
            "phoneme_comparison": [
                {
                    "position": i + 1,
                    "target": phoneme,
                    "user": "",
                    "status": "missing",
                    "similarity_score": 0,
                    "feedback": "Not pronounced"
                }
                for i, phoneme in enumerate(target_list)
            ],
            "specific_issues": [
                {
                    "phoneme": "all",
                    "issue": "No audio detected or silent recording",
                    "suggestion": "Please check your microphone and try recording again"
                }
            ],
            "strengths": [],
            "improvement_tips": [
                "Ensure your microphone is working properly",
                "Speak clearly and at normal volume",
                "Check recording permissions"
            ],
            "intelligibility_level": "Beginner",
            "confidence_level": "Low",
            "alignment_analysis": {
                "total_phonemes_target": total_target,
                "total_phonemes_user": 0,
                "correct_phonemes": 0,
                "similar_phonemes": 0,
                "incorrect_phonemes": 0,
                "missing_phonemes": total_target,
                "extra_phonemes": 0
            },
            "method": "simple_fallback_empty_audio"
        }
    
    # Simple analysis for non-empty user phonemes
    length_diff = abs(total_target - total_user)
    base_score = max(0, 100 - (length_diff * 10))
    
    return {
        "accuracy_score": base_score,
        "native_understandable": base_score >= 70,
        "overall_feedback": f"Basic analysis: {base_score}% accuracy estimate",
        "phoneme_comparison": [],
        "specific_issues": [
            {
                "phoneme": "general",
                "issue": "Detailed analysis unavailable",
                "suggestion": "Continue practicing pronunciation"
            }
        ],
        "strengths": ["Pronunciation attempt recorded"],
        "improvement_tips": ["Practice with native speakers", "Record yourself regularly"],
        "intelligibility_level": "Intermediate" if base_score >= 70 else "Beginner",
        "confidence_level": "Low",
        "alignment_analysis": {
            "total_phonemes_target": total_target,
            "total_phonemes_user": total_user,
            "correct_phonemes": 0,
            "similar_phonemes": 0,
            "incorrect_phonemes": 0,
            "missing_phonemes": max(0, total_target - total_user),
            "extra_phonemes": max(0, total_user - total_target)
        },
        "method": "simple_fallback"
    }

async def analyze_pronunciation(audio_data: bytes, id_content: int, db: Session, content_type: str = "sentence") -> Dict[str, any]:
    """Main function - PURE GEMINI ANALYSIS"""
    try:
        # Process audio to get phonemes
        audio = audio_processor.preprocess_audio(audio_data)
        user_phonemes = audio_processor.infer_phonemes(audio)
        
        # Get target phonemes from text
        # target_phonemes = text_to_ipa_gruut(target_text)
        if content_type == "sentence":
            content = db.query(Materifonemkalimat).filter(
                Materifonemkalimat.idmaterifonemkalimat == id_content
            ).first()
            
            if not content:
                return {"error": "Sentence content not found in database"}
            
            target_text = content.kalimat
            # Use database phoneme if available, otherwise generate from text
            target_phonemes = content.fonem
            
        elif content_type == "word":
            content = db.query(Materifonemkata).filter(
                Materifonemkata.idmaterifonemkata == id_content
            ).first()
            
            if not content:
                return {"error": "Word content not found in database"}
            
            target_text = content.kata
            # Use database phoneme if available, otherwise generate from text
            target_phonemes = content.fonem if content.fonem else text_to_ipa_gruut(target_text)

        elif content_type == "exam":
            content = db.query(Materiujiankalimat).filter(
                Materiujiankalimat.idmateriujiankalimat == id_content
            ).first()
            
            if not content:
                return {"error": "Word content not found in database"}
            
            target_text = content.kalimat
            # Use database phoneme if available, otherwise generate from text
            target_phonemes = content.fonem if content.fonem else text_to_ipa_gruut(target_text)

        else:
            return {"error": "Invalid content type"}
        
        target_phonemes_separated = separate_phonemes(target_phonemes)
        logger.info(f"Target phonemes: {target_phonemes}")
        logger.info(f"User phonemes: {user_phonemes}")
        
        # Use ONLY Gemini for analysis
        gemini_analysis = await analyze_phonemes_with_gemini(
            target_phonemes_separated, user_phonemes, target_text
        )
        
        # If Gemini fails, use simple fallback (no SequenceMatcher)
        if "error" in gemini_analysis:
            logger.warning(f"Gemini analysis failed: {gemini_analysis['error']}")
            fallback_result = create_simple_fallback_analysis(target_phonemes_separated, user_phonemes)
            fallback_result["gemini_error"] = gemini_analysis["error"]
            return {
                "target_phonemes": target_phonemes_separated,
                "user_phonemes": user_phonemes,
                "analysis": fallback_result
            }
        
        # Return successful Gemini analysis
        return {
            "target_phonemes": target_phonemes_separated,
            "user_phonemes": user_phonemes,
            "analysis": gemini_analysis
        }
        
    except Exception as e:
        logger.error(f"Error in pronunciation analysis: {str(e)}")
        return {
            "error": f"Analysis error: {str(e)}",
            "target_phonemes": "",
            "user_phonemes": "",
            "analysis": {}
        }

def separate_phonemes(phoneme_string: str) -> str:

    VOWEL_PHONEMES = [
        "i", "ɪ", "ɛ", "æ", "ə", "ɚ", "ʌ", "ɔ", "ʊ", "u"
    ]
    
    DIPHTHONG_PHONEMES = [
        "eɪ", "aɪ", "ɔɪ", "aʊ", "oʊ"
    ]
    
    CONSONANT_PHONEMES = [
        "p", "b", "t", "d", "k", "g", "f", "v", "θ", "ð",
        "s", "z", "ʃ", "ʒ", "tʃ", "dʒ", "h", "m", "n", "ŋ", "l", "r", "j", "w"
    ]
    
    # Simbol yang akan dihapus
    SYMBOLS_TO_REMOVE = ["ː", "ˈ"]
    
    # Gabungkan semua fonem dan urutkan berdasarkan panjang (yang lebih panjang dulu)
    all_phonemes = DIPHTHONG_PHONEMES + CONSONANT_PHONEMES + VOWEL_PHONEMES
    all_phonemes.sort(key=len, reverse=True)
    
    if not phoneme_string:
        return ""
    
    separated_phonemes = []
    i = 0
    
    while i < len(phoneme_string):
        found_phoneme = False
        
        # Skip simbol yang harus dihapus
        if phoneme_string[i] in SYMBOLS_TO_REMOVE:
            i += 1
            continue
        
        # Cari fonem yang cocok dimulai dari posisi i
        for phoneme in all_phonemes:
            if phoneme_string[i:i+len(phoneme)] == phoneme:
                separated_phonemes.append(phoneme)
                i += len(phoneme)
                found_phoneme = True
                break
        
        # Jika tidak ditemukan fonem yang cocok, ambil karakter tunggal
        if not found_phoneme:
            separated_phonemes.append(phoneme_string[i])
            i += 1
    
    return " ".join(separated_phonemes)


def text_to_ipa_gruut(text: str, lang: str = "en-us") -> str:
    """Convert text to IPA phonemes using gruut"""
    phonemes = []
    for sentence in sentences(text, lang=lang, phonemes=True):
        for word in sentence.words:
            if word.phonemes:
                phonemes.extend(word.phonemes)
    
    normalized = normalize_tie_bar_phonemes(phonemes)
    processed_phonemes = reconstruct_diphthongs(normalized)
    return " ".join(processed_phonemes)

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


SIMILAR_PHONEMES = {
    # Vowel Pairs
    "i": ["ɪ"],
    "ɪ": ["i", "ɛ"],
    "ɛ": ["æ", "ɪ"],
    "æ": ["ɛ"],
    "ə": ["ʌ", "ɚ"],
    "ɚ": ["ə", "ʌ"],
    "ʌ": ["ə", "ɚ"],
    "ɔ": ["oʊ"],
    "oʊ": ["ɔ", "ʊ"],
    "ʊ": ["u", "oʊ"],
    "u": ["ʊ"],
    # Diphthong Pairs (based on ending/starting vowels)
    "eɪ": ["ɛ", "ɪ"],
    "aɪ": ["ɪ"],
    "ɔɪ": ["ɔ", "ɪ"],
    "aʊ": ["ʊ"],
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