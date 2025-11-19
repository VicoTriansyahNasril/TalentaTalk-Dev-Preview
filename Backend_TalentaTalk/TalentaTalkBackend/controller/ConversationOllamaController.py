# ConversationOllamaController.py
import random
import aiohttp
import asyncio
import re
from sqlalchemy.ext.asyncio import AsyncSession
from models import Materipercakapan, Hasillatihanpercakapan
from datetime import datetime
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import json

# Pastikan folder log ada
os.makedirs("log", exist_ok=True)

# Setup logger ke file
logging.basicConfig(
    filename="log/hasil_chat.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="a"  # tambah ke akhir file, bukan overwrite
)

logger = logging.getLogger(__name__)

# Session storage untuk menyimpan context per sesi
conversation_sessions: Dict[str, Dict[str, Any]] = {}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_or_create_session(session_id: str = "conversation") -> Dict[str, Any]:
    """Get or create a session context"""
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "chat_context": [],
            "confidence_report": [],
            "current_topic": "",
            "generated_question": ""
        }
    return conversation_sessions[session_id]

async def generate_question_with_gemini(topic: str) -> str:
    """Generate a conversation starter question based on topic using Gemini API"""
    try:
        logger.info(f"Calling Gemini API for topic: '{topic}'")
        
        # Check if API key is set
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE": #
            logger.error("Gemini API key not set properly")
            return f"Can you tell me about your experience with {topic}?"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Generate a different question each time by adding variety instructions
        prompt = f"""
        Based on the IT topic: "{topic}"
        
        Generate a unique, engaging conversation starter question that:
        1. Is directly related to the IT topic "{topic}"
        2. Encourages detailed discussion about IT projects, technical experiences, or programming challenges
        3. Is suitable for professional IT conversation practice
        4. Is open-ended and allows for personal technical experience sharing
        5. MUST be in American English (US English) only
        6. Make it different from typical questions - be creative and specific to IT domain
        7. Focus on practical IT experience, real-world technical scenarios, coding problems, or system implementation
        8. Should encourage discussion about programming languages, frameworks, databases, cloud services, DevOps, cybersecurity, or other IT technologies
        
        Examples of IT-specific question styles:
        - "What was the most challenging bug you encountered when working with..."
        - "How did you optimize performance when dealing with..."
        - "Can you walk me through your approach to implementing..."
        - "What would you do differently if you had to architect..."
        - "Describe a time when you had to troubleshoot..."
        - "How do you handle version control when..."
        - "What's your experience with deploying..."
        
        Return only one creative IT-focused question in American English, nothing else.
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        logger.info(f"Making request to Gemini API: {GEMINI_API_URL}")
        
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                logger.info(f"Gemini API response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Gemini API response data keys: {list(data.keys())}")
                    
                    generated_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    if generated_text:
                        # Clean up the generated question
                        question = generated_text.strip()
                        logger.info(f"Successfully generated question with Gemini: {question}")
                        return question
                    else:
                        logger.warning("Empty response from Gemini API")
                        return f"Can you tell me about your experience with {topic}?"
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error {response.status}: {error_text}")
                    return f"Can you tell me about your experience with {topic}?"
                    
    except asyncio.TimeoutError:
        logger.error("Gemini API timeout")
        return f"Can you tell me about your experience with {topic}?"
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Can you tell me about your experience with {topic}?"

async def get_random_topic(db: AsyncSession, session_id: str = "conversation") -> str:
    """Get random topic from database and generate NEW question with Gemini each time"""
    from sqlalchemy import select
    
    try:
        # Add more detailed logging for debugging
        logger.info("Starting get_random_topic function")
        
        # Check if db is actually AsyncSession or regular Session
        logger.info(f"Database session type: {type(db)}")
        
        # Handle both sync and async database sessions
        if hasattr(db, 'execute') and hasattr(db, 'commit'):
            # This might be a sync session
            try:
                result = db.execute(select(Materipercakapan))
                topics = result.scalars().all()
            except Exception as sync_error:
                logger.info(f"Sync query failed, trying async: {sync_error}")
                # Try async approach
                result = await db.execute(select(Materipercakapan))
                topics = result.scalars().all()
        else:
            # Assume it's async
            result = await db.execute(select(Materipercakapan))
            topics = result.scalars().all()
        
        logger.info(f"Found {len(topics) if topics else 0} topics in database")
        
        if not topics:
            logger.warning("No topics found in database, using fallback")
            fallback_topic = "IT Project Management"
            session_data = get_or_create_session(session_id)
            session_data["current_topic"] = fallback_topic
            session_data["generated_question"] = await generate_question_with_gemini(fallback_topic)
            return session_data["generated_question"]
        
        # Log all available topics
        for i, topic in enumerate(topics):
            logger.info(f"Topic {i+1}: {topic.topic}")
        
        # Get a random topic from database
        selected_topic = random.choice(topics)
        session_data = get_or_create_session(session_id)
        session_data["current_topic"] = selected_topic.topic
        
        logger.info(f"Selected topic: '{selected_topic.topic}'")
        logger.info(f"About to call Gemini API for topic: '{selected_topic.topic}'")
        
        # ALWAYS generate a NEW question based on the topic using Gemini
        # Even if it's the same topic, Gemini will create different questions
        try:
            generated_question = await generate_question_with_gemini(selected_topic.topic)
            session_data["generated_question"] = generated_question
            
            logger.info(f"Successfully generated NEW question: {generated_question}")
            return generated_question
            
        except Exception as gemini_error:
            logger.error(f"Gemini API failed: {str(gemini_error)}")
            # Fallback to simple question if Gemini fails
            fallback_question = f"Can you tell me about your experience with {selected_topic.topic}?"
            session_data["generated_question"] = fallback_question
            return fallback_question
        
    except Exception as e:
        logger.error(f"Error in get_random_topic: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        fallback_question = "Can you describe an IT project you've worked on recently?"
        session_data = get_or_create_session(session_id)
        session_data["current_topic"] = "General IT Discussion"
        session_data["generated_question"] = fallback_question
        return fallback_question

async def start_chat(db, session_id: str = "conversation") -> str:
    """Start a new chat session with randomized topic and Gemini-generated question"""
    try:
        # Get random topic and generate NEW question using Gemini
        generated_question = await get_random_topic(db, session_id)
        
        session_data = get_or_create_session(session_id)
        
        # UPDATED SYSTEM PROMPT - More conversational and concise
        system_prompt = f"""
        You are a friendly conversation partner practicing English with an IT professional.
        
        IMPORTANT RULES:
        - Keep ALL responses SHORT (maximum 2-3 sentences)
        - NO code examples, NO technical tutorials, NO long explanations
        - Be conversational and casual like a friend
        - Ask simple follow-up questions about their experience
        - Focus on their personal experience with {session_data["current_topic"]}
        - Respond naturally like in a real conversation
        - Encourage them to share more about their work experience
        
        Current topic: {session_data["current_topic"]}
        Start with: "{generated_question}"
        
        Example response style:
        "That sounds interesting! How long have you been working with that technology?"
        "Nice! What was the most challenging part about that project?"
        """
        
        session_data["chat_context"].clear()
        session_data["confidence_report"].clear()
        session_data["chat_context"].append({"role": "system", "content": system_prompt})
        
        logger.info(f"Started new chat session with topic: {session_data['current_topic']}")
        logger.info(f"Using NEW generated question: {generated_question}")
        
        return generated_question
        
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        raise
    
def calculate_wpm(text: str, duration: str) -> float:
    """Calculate words per minute"""
    try:
        words = len(text.split())
        # Handle different duration formats
        duration = duration.strip()
        
        if ':' in duration:
            time_parts = duration.split(':')
            if len(time_parts) == 2:
                minutes, seconds = map(int, time_parts)
                total_seconds = minutes * 60 + seconds
            else:
                logger.warning(f"Invalid duration format: {duration}")
                return 0.0
        else:
            # Assume it's just seconds
            total_seconds = int(duration)
        
        if total_seconds <= 0:
            return 0.0
            
        wpm = (words / total_seconds) * 60
        logger.info(f"Calculated WPM: {wpm:.2f} for {words} words in {total_seconds} seconds")
        return round(wpm, 2)
    except (ValueError, AttributeError, ZeroDivisionError) as e:
        logger.error(f"Error calculating WPM: {str(e)}")
        return 0.0

async def check_grammar(text: str) -> str:
    """Check grammar using LanguageTool API"""
    url = "https://api.languagetool.org/v2/check"
    params = {"text": text, "language": "en-US"}
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=params) as response:
                if response.status == 200:
                    data = await response.json()
                    errors = data.get("matches", [])
                    result = "Grammar issues found." if errors else "Grammar is correct."
                    logger.info(f"Grammar check result: {result}")
                    return result
                else:
                    logger.warning(f"Grammar API returned status {response.status}")
                    return "Error checking grammar."
    except asyncio.TimeoutError:
        logger.error("Grammar check timeout")
        return "Grammar check timeout."
    except Exception as e:
        logger.error(f"Grammar check error: {str(e)}")
        return "Error checking grammar."

async def send_to_gemini(session_id: str = "conversation") -> Tuple[Optional[str], Optional[str]]:
    """Send message to Gemini API with improved conversational prompts"""
    session_data = get_or_create_session(session_id)
    
    try:
        # Check if API key is set
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            return None, "Gemini API key not set properly"
        
        # Convert chat context to Gemini format
        gemini_contents = []
        system_context = ""
        
        # Extract system context first
        for msg in session_data["chat_context"]:
            if msg["role"] == "system":
                system_context = msg["content"]
                break
        
        # Convert messages to Gemini format (user/model roles only)
        user_messages = []
        assistant_messages = []
        
        for msg in session_data["chat_context"]:
            if msg["role"] == "user":
                user_messages.append(msg["content"])
            elif msg["role"] == "assistant":
                assistant_messages.append(msg["content"])
        
        # Build conversation history in Gemini format
        for i in range(max(len(user_messages), len(assistant_messages))):
            # Add user message
            if i < len(user_messages):
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": user_messages[i]}]
                })
            
            # Add model response
            if i < len(assistant_messages):
                gemini_contents.append({
                    "role": "model", 
                    "parts": [{"text": assistant_messages[i]}]
                })
        
        # Enhanced system context for better conversation flow
        if system_context and len(gemini_contents) > 0:
            # Add enhanced instructions to the conversation
            conversation_instruction = f"""
            {system_context}
            
            CRITICAL INSTRUCTIONS:
            - Keep your response SHORT (maximum 20-30 words)
            - NO code examples or technical tutorials
            - Be friendly and conversational
            - Ask ONE simple follow-up question
            - Focus on their personal experience
            - Respond like you're having a casual chat with a colleague
            
            User's message: {gemini_contents[-1]["parts"][0]["text"] if gemini_contents else ""}
            """
            
            # Replace the last user message with enhanced instruction
            if gemini_contents:
                gemini_contents[-1]["parts"][0]["text"] = conversation_instruction
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 100,  # REDUCED from 1024 to 100 for shorter responses
                "stopSequences": ["\n\n", "```"]  # Stop at double newlines or code blocks
            }
        }
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        logger.info(f"Making request to Gemini API for chat response")
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                logger.info(f"Gemini API chat response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    generated_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    if generated_text:
                        # Clean and truncate response if too long
                        cleaned_response = generated_text.strip()
                        
                        # Remove any code blocks if they somehow appear
                        cleaned_response = re.sub(r'```.*?```', '', cleaned_response, flags=re.DOTALL)
                        cleaned_response = re.sub(r'`[^`]*`', '', cleaned_response)
                        
                        # Truncate if too long (more than 150 characters)
                        if len(cleaned_response) > 150:
                            sentences = cleaned_response.split('. ')
                            cleaned_response = '. '.join(sentences[:2])
                            if not cleaned_response.endswith('.'):
                                cleaned_response += '.'
                        
                        logger.info(f"Gemini chat response received: {len(cleaned_response)} characters")
                        return cleaned_response, None
                    else:
                        logger.warning("Empty response from Gemini API")
                        return None, "Empty response from Gemini API"
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error {response.status}: {error_text}")
                    return None, f"Gemini API error {response.status}: {error_text}"
                    
    except asyncio.TimeoutError:
        error_msg = "Gemini API request timeout"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Gemini API request error: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    
async def process_user_input(user_input: str, duration: str, session_id: str = "conversation") -> Dict[str, Any]:
    """Process user input and generate response"""
    try:
        session_data = get_or_create_session(session_id)
        
        wpm = calculate_wpm(user_input, duration)
        confidence_score = min(100, max(0, round(wpm)))
        grammar_result = await check_grammar(user_input)
        
        session_data["confidence_report"].append({
            "text": user_input,
            "wpm": wpm,
            "confidence_score": confidence_score,
            "grammar": grammar_result
        })
        
        session_data["chat_context"].append({"role": "user", "content": user_input})
        ai_response, error = await send_to_gemini(session_id)  # Changed from send_to_llm to send_to_gemini
        
        if error:
            logger.error(f"Gemini Error: {error}")
            return {"error": "Gemini Error", "detail": error}
        
        session_data["chat_context"].append({"role": "assistant", "content": ai_response})
        
        result = {
            "response": ai_response,
            "confidence_score": confidence_score,
            "grammar_check": grammar_result,
        }
        
        logger.info(f"Processed user input successfully. Confidence: {confidence_score}, Grammar: {grammar_result}")
        return result
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        return {"error": "Processing Error", "detail": str(e)}

async def get_detailed_report(session_id: str = "conversation") -> Dict[str, List[Dict[str, Any]]]:
    """Get detailed report with grammar analysis"""
    session_data = get_or_create_session(session_id)
    detailed_report = []
    
    for entry in session_data["confidence_report"]:
        user_text = entry["text"]
        url = "https://api.languagetool.org/v2/check"
        params = {"text": user_text, "language": "en-US"}
        grammar_issues = []
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, data=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        matches = data.get("matches", [])
                        for m in matches:
                            grammar_issues.append({
                                "message": m.get("message", ""),
                                "suggestions": [s.get("value", "") for s in m.get("replacements", [])],
                                "sentence": m.get("sentence", "")
                            })
        except Exception as e:
            logger.error(f"Grammar analysis error: {str(e)}")
        
        detailed_report.append({
            "user_input": user_text,
            "wpm_confidence_info": f"User said: '{user_text}' | WPM: {entry['wpm']:.2f} | Confidence Score: {entry['confidence_score']} | Grammar: {entry['grammar']}",
            "grammar_issues": grammar_issues
        })
    
    return {"report": detailed_report}

async def save_report_to_db(db: AsyncSession, talent_id: int, session_id: str = "conversation") -> Dict[str, Any]:
    """Save conversation report to database"""
    from sqlalchemy import select
    
    try:
        session_data = get_or_create_session(session_id)
        
        if not session_data["confidence_report"]:
            return {"success": False, "message": "No conversation data to save"}
        
        # Get materipercakapan id by topic
        result = await db.execute(
            select(Materipercakapan).filter(Materipercakapan.topic == session_data["current_topic"])
        )
        materi = result.scalar_one_or_none()
        
        if not materi:
            logger.error(f"Topic '{session_data['current_topic']}' not found in database")
            return {"success": False, "message": f"Topic '{session_data['current_topic']}' not found in database"}
        
        # Calculate average WPM
        total_wpm = sum(entry["wpm"] for entry in session_data["confidence_report"])
        avg_wpm = total_wpm / len(session_data["confidence_report"]) if session_data["confidence_report"] else 0
        
        # Combine grammar issues into a string with messages and suggestions
        grammar_issues = []
        for entry in session_data["confidence_report"]:
            # Get detailed grammar issues
            user_text = entry["text"]
            url = "https://api.languagetool.org/v2/check"
            params = {"text": user_text, "language": "en-US"}
            
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, data=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            matches = data.get("matches", [])
                            for m in matches:
                                suggestion = m.get("replacements", [])
                                suggestion_text = suggestion[0]["value"] if suggestion else "No suggestion"
                                issue = f"{m.get('message')} - Suggestion: {suggestion_text}"
                                grammar_issues.append(issue)
            except Exception as e:
                logger.error(f"Grammar analysis error in save: {str(e)}")
        
        # Limit grammar string to 255 characters
        grammar_str = "; ".join(grammar_issues)
        if len(grammar_str) > 255:
            grammar_str = grammar_str[:252] + "..."
        
        # Create new record
        new_result = Hasillatihanpercakapan(
            idtalent=talent_id,
            idmateripercakapan=materi.idmateripercakapan,
            wpm=avg_wpm,
            grammar=grammar_str if grammar_issues else "No grammar issues found",
            waktulatihan=datetime.now()
        )

        db.add(new_result)
        await db.commit()
        logger.info(f"Saved conversation result for talent {talent_id}, topic: {session_data['current_topic']}")
        return {"success": True, "message": "Conversation results saved successfully"}

    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving conversation result: {str(e)}")
        return {"success": False, "message": f"Database error: {str(e)}"}

def clear_session(session_id: str = "conversation") -> Dict[str, Any]:
    """Clear session data"""
    try:
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
            logger.info(f"Session '{session_id}' cleared")
        return {"success": True, "message": f"Session '{session_id}' cleared"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        return {"success": False, "message": f"Error clearing session: {str(e)}"}