import aiohttp
import logging
import json
import re
from typing import Dict, Any, List
from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

class LLMService:
    HEADERS = {"Content-Type": "application/json"}

    @staticmethod
    def _clean_json_string(text: str) -> str:
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return text.strip()

    @staticmethod
    async def _send_request(payload: dict) -> str:
        url = f"{settings.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=LLMService.HEADERS, 
                    timeout=30
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Gemini API Error ({response.status}): {error_text}")
                        if response.status == 429:
                            raise AppError(status_code=429, detail="AI Traffic Limit Exceeded")
                        raise AppError(status_code=502, detail="AI Service Provider Error")
                    
                    data = await response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError):
                        logger.error(f"Unexpected API Response format: {data}")
                        return "{}"
        except Exception as e:
            logger.error(f"LLM Network Error: {e}")
            if isinstance(e, AppError):
                raise e
            return "{}"
    
    @staticmethod
    async def generate(prompt_text: str) -> str:
        return await LLMService._send_request({
            "contents": [{"parts": [{"text": prompt_text}]}]
        })

    @staticmethod
    async def generate_with_history(history: List[Dict[str, str]], system_prompt: str) -> str:
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        if contents and contents[-1]["role"] == "user":
            contents[-1]["parts"][0]["text"] += f"\n\nSYSTEM INSTRUCTION: {system_prompt}"
        else:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {system_prompt}"}]})

        return await LLMService._send_request({"contents": contents})

    @staticmethod
    async def generate_interview_followup(prev_question: str, answer: str) -> Dict[str, Any]:
        prompt = f"""
        SYSTEM ROLE: Technical Recruiter.
        Context: Q: "{prev_question}" A: "{answer}"
        Task: 1 sentence feedback, 1 probing follow-up question.
        Return JSON: {{ "feedback": "...", "followup_question": "..." }}
        """
        raw = await LLMService.generate(prompt)
        try:
            return json.loads(LLMService._clean_json_string(raw))
        except:
            return {"feedback": "Thank you.", "followup_question": "Can you elaborate?"}

    @staticmethod
    async def generate_interview_feedback(history: List[Dict[str, str]]) -> Dict[str, Any]:
        history_text = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in history])
        prompt = f"""
        Analyze this interview transcript:
        {history_text}
        
        Return JSON:
        {{
            "summary": {{
                "strengths": ["pt1", "pt2"],
                "weaknesses": ["pt1", "pt2"],
                "overall_performance": {{
                    "technical_knowledge": "Good/Fair/Poor",
                    "communication_speed": "Fast/Avg/Slow",
                    "grammar_usage": "Good/Bad",
                    "recommendation": "Hire/No Hire"
                }}
            }}
        }}
        """
        raw = await LLMService.generate(prompt)
        try:
            return json.loads(LLMService._clean_json_string(raw))
        except:
            return {"summary": {}}

    @staticmethod
    async def check_relevance(question: str, answer: str) -> Dict[str, Any]:
        prompt = f"""
        Question: "{question}" Answer: "{answer}"
        Is the answer logically relevant?
        Return JSON: {{ "is_relevant": true/false, "reason": "..." }}
        """
        raw = await LLMService.generate(prompt)
        try:
            return json.loads(LLMService._clean_json_string(raw))
        except:
            return {"is_relevant": True}

    @staticmethod
    async def analyze_phoneme_quality(target: str, user: str, text: str) -> Dict[str, Any]:
        prompt = f"""
        Phonetic Analysis.
        Text: "{text}"
        Target IPA: {target}
        User IPA: {user}
        
        Return JSON:
        {{
            "native_understandable": true/false,
            "overall_feedback": "string",
            "specific_issues": [{{"phoneme": "p", "issue": "desc", "suggestion": "tip"}}],
            "strengths": ["list"],
            "improvement_tips": ["list"]
        }}
        """
        raw = await LLMService.generate(prompt)
        try:
            return json.loads(LLMService._clean_json_string(raw))
        except:
            return {}