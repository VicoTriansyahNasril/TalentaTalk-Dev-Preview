import aiohttp
import logging
import json
import re
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

class LLMService:
    GEMINI_URL = f"{settings.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"
    HEADERS = {"Content-Type": "application/json"}

    @staticmethod
    def _clean_json_string(text: str) -> str:
        """Membersihkan markdown formatting dari response LLM"""
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return text.strip()

    @staticmethod
    async def _send_request(payload: dict) -> str:
        if not settings.GEMINI_API_KEY:
            raise AppError(status_code=503, detail="AI Service configuration missing")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    LLMService.GEMINI_URL, 
                    json=payload, 
                    headers=LLMService.HEADERS, 
                    timeout=30
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Gemini API Error: {error_text}")
                        raise AppError(status_code=502, detail="AI Service Provider Error")
                    
                    data = await response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError):
                        logger.error(f"Unexpected API Response format: {data}")
                        return "{}"
        except Exception as e:
            logger.error(f"LLM Network Error: {e}")
            raise AppError(status_code=503, detail="AI Service Timeout")

    @staticmethod
    async def generate_chat_response(user_input: str, topic: str) -> Dict[str, Any]:
        prompt = f"""
        SYSTEM ROLE: You are an expert English Tutor specializing in '{topic}'.
        
        USER INPUT: "{user_input}"
        
        YOUR TASK:
        1. Analyze the user's grammar.
        2. Provide a natural, encouraging conversational response to keep the chat going.
        3. Suggest 2-3 better ways to phrase the input.
        
        FORMAT RESTRICTION: Return ONLY a raw JSON object. Do not include markdown formatting.
        {{
            "grammar_check": "Correct" or "Correction: [correction]",
            "response": "[Your natural reply]",
            "suggestions": ["[Suggestion 1]", "[Suggestion 2]"]
        }}
        """
        raw_text = await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        })
        
        try:
            return json.loads(LLMService._clean_json_string(raw_text))
        except json.JSONDecodeError:
            return {
                "grammar_check": "Analysis unavailable", 
                "response": "I understood that, but I'm having trouble analyzing the grammar right now. Let's continue!", 
                "suggestions": []
            }

    @staticmethod
    async def generate(prompt_text: str) -> str:
        """Generic text generation helper"""
        raw_text = await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt_text}]}]
        })
        return raw_text

    @staticmethod
    async def generate_interview_followup(prev_question: str, answer: str) -> Dict[str, Any]:
        prompt = f"""
        SYSTEM ROLE: You are a Senior Technical Recruiter conducting a professional interview.
        
        CONTEXT:
        Question: "{prev_question}"
        Candidate Answer: "{answer}"
        
        YOUR TASK:
        1. Provide brief, professional feedback (1 sentence).
        2. Ask a relevant, probing follow-up question based strictly on the candidate's answer.
        
        FORMAT RESTRICTION: Return ONLY a raw JSON object.
        {{
            "feedback": "[Professional feedback]",
            "followup_question": "[Deep dive question]"
        }}
        """
        raw_text = await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt}]}]
        })
        try:
            return json.loads(LLMService._clean_json_string(raw_text))
        except json.JSONDecodeError:
            return {
                "feedback": "Thank you for sharing that.", 
                "followup_question": "Could you elaborate more on the technical challenges?"
            }

    @staticmethod
    async def generate_interview_feedback(history: List[Dict[str, str]]) -> Dict[str, Any]:
        history_text = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in history])
        prompt = f"""
        SYSTEM ROLE: You are a Hiring Manager analyzing an interview transcript.
        
        TRANSCRIPT:
        {history_text}
        
        YOUR TASK: Provide a comprehensive performance review.
        
        FORMAT RESTRICTION: Return ONLY a raw JSON object.
        {{
            "summary": {{
                "strengths": ["Point 1", "Point 2"],
                "weaknesses": ["Point 1", "Point 2"],
                "overall_performance": {{
                    "technical_knowledge": "Good/Fair/Poor",
                    "communication_speed": "Fast/Average/Slow",
                    "grammar_usage": "Good/Needs Improvement",
                    "recommendation": "Hire/No Hire/Train"
                }}
            }}
        }}
        """
        raw_text = await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4}
        })
        try:
            return json.loads(LLMService._clean_json_string(raw_text))
        except json.JSONDecodeError:
            return {"summary": {}}

    @staticmethod
    async def analyze_phoneme_quality(target: str, user: str, text: str) -> Dict[str, Any]:
        prompt = f"""
        SYSTEM ROLE: You are a Linguistic Expert in Phonetics.
        
        TASK: Compare pronunciation.
        - Text: "{text}"
        - Target IPA: {target}
        - User IPA: {user}
        
        FORMAT RESTRICTION: Return ONLY a raw JSON object.
        {{
            "native_understandable": true/false,
            "overall_feedback": "Brief linguistic feedback",
            "specific_issues": [
                {{"phoneme": "target_phoneme", "issue": "explanation", "suggestion": "tip"}}
            ],
            "strengths": ["list of strengths"],
            "improvement_tips": ["tip 1", "tip 2"]
        }}
        """
        raw_text = await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt}]}]
        })
        try:
            return json.loads(LLMService._clean_json_string(raw_text))
        except json.JSONDecodeError:
            return {}

    @staticmethod
    async def check_relevance(question: str, answer: str) -> Dict[str, Any]:
        """Check if answer is on-topic"""
        prompt = f"""
        SYSTEM ROLE: Context Analyzer.
        
        Question: "{question}"
        Candidate Answer: "{answer}"
        
        TASK: Determine if the answer is logically relevant to the question. 
        - Even brief answers ("I don't know") are RELEVANT.
        - Only mark IRRELEVANT if it talks about a completely different topic (e.g., cooking instead of coding).
        
        FORMAT RESTRICTION: Return ONLY a raw JSON object.
        {{ "is_relevant": true/false, "reason": "short explanation" }}
        """
        raw = await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt}]}]
        })
        try:
            return json.loads(LLMService._clean_json_string(raw))
        except:
            return {"is_relevant": True}