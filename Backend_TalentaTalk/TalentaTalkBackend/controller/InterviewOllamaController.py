# InterviewOllamaController.py - Updated with Off-Topic Detection
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from models import Materiinterview, Hasillatihaninterview
from database import get_db  # fungsi untuk mendapatkan session database
import aiohttp  # Untuk membuat permintaan HTTP async ke API
import json     # Untuk memanipulasi data dalam format JSON
from datetime import datetime  # Untuk bekerja dengan tanggal dan waktu
from sessions import get_session
import re       # For regular expression processing
import os       # For environment variables
import asyncio
from typing import Dict, Any, List

app = FastAPI()

# Menambahkan middleware session
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

interview_topic = "Interview"

# Global session storage
conversation_sessions: Dict[str, Dict[str, Any]] = {}

def get_session_id(request) -> str:
    """Generate or get session ID for conversation tracking"""
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = f"session_{datetime.now().timestamp()}"
        request.session["session_id"] = session_id
    return session_id

async def call_gemini_api_async(messages: List[Dict], system_instruction: str = None) -> Dict[str, Any]:
    """
    Fungsi async untuk memanggil Gemini API dengan format yang benar
    """
    # Convert messages to Gemini format 
    contents = []
    
    # Gabungkan system instruction dengan context jika ada
    if system_instruction:
        # Tambahkan system instruction sebagai bagian dari conversation
        full_context = system_instruction + "\n\n"
        
        # Gabungkan semua pesan menjadi satu konteks
        for msg in messages:
            if msg.get("role") == "system":
                continue  # Skip system messages karena sudah digabung
            elif msg.get("role") == "assistant":
                full_context += f"AI: {msg.get('content', '')}\n\n"
            elif msg.get("role") == "user":
                full_context += f"Human: {msg.get('content', '')}\n\n"
        
        contents.append({
            "parts": [{"text": full_context.strip()}]
        })
    else:
        # Jika tidak ada system instruction, proses pesan normal
        for msg in messages:
            if msg.get("role") in ["user", "assistant"]:
                contents.append({
                    "parts": [{"text": msg.get("content", "")}]
                })
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if "candidates" in result and len(result["candidates"]) > 0:
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        return {"success": True, "content": content.strip()}
                    else:
                        return {"success": False, "error": "No response from Gemini"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"API Error: {response.status} - {error_text}"}
                    
    except aiohttp.ClientError as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

async def check_answer_relevance(question: str, answer: str) -> Dict[str, Any]:
    """
    Check if the answer is relevant to the question using Gemini API
    """
    relevance_instruction = f"""
    You are an interview evaluator. Analyze whether the candidate's answer is relevant to the interview question asked.

    Question: "{question}"
    Answer: "{answer}"

    Determine if the answer is:
    1. ON-TOPIC: The answer directly addresses the question asked, even if brief or incomplete
    2. OFF-TOPIC: The answer is completely unrelated to the question, talks about irrelevant subjects, or doesn't attempt to address the question

    Guidelines:
    - Consider the answer ON-TOPIC if it makes any reasonable attempt to address the question
    - Consider the answer OFF-TOPIC only if it's completely unrelated (talking about weather, food, personal life unrelated to work, etc.)
    - Brief answers or "I don't know" responses should be considered ON-TOPIC
    - Partial answers or tangential responses should be considered ON-TOPIC

    Provide your response in this EXACT JSON format:
    {{
        "is_relevant": true/false,
        "reason": "Brief explanation of why the answer is on-topic or off-topic"
    }}
    """
    
    response = await call_gemini_api_async([], relevance_instruction)
    
    if response["success"]:
        try:
            # Try to parse JSON from response
            content = response["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                relevance_data = json.loads(json_match.group())
                return {
                    "is_relevant": relevance_data.get("is_relevant", True),
                    "reason": relevance_data.get("reason", "Answer evaluated")
                }
        except Exception as e:
            print(f"Error parsing relevance check: {e}")
    
    # Fallback - assume relevant if API fails
    return {"is_relevant": True, "reason": "Unable to evaluate relevance"}

def parse_duration_to_seconds(duration_str: str) -> int:
    """
    Convert duration string (MM:SS) to total seconds
    """
    try:
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
        return int(float(duration_str))  # If it's just seconds
    except:
        return 0

def calculate_wpm(answer_text: str, duration_seconds: int) -> float:
    """
    Calculate WPM only (grammar will be calculated in summary)
    """
    if duration_seconds <= 0:
        return 0.0
    
    # Count words
    word_count = len(answer_text.split())
    
    # Calculate WPM
    return round((word_count / duration_seconds) * 60, 1)

async def analyze_grammar_and_wpm_batch(all_answers: List[Dict]) -> Dict[str, Any]:
    """
    Analyze grammar and calculate WPM for all answers in one Gemini API call
    """
    if not all_answers:
        return {"grammar_analysis": [], "overall_wpm": 0}
    
    # Prepare text for batch analysis
    analysis_text = "Analyze the grammar quality for each of the following interview responses:\n\n"
    
    for i, answer in enumerate(all_answers, 1):
        analysis_text += f"Response {i}:\nQuestion: {answer['question']}\nAnswer: {answer['answer']}\nDuration: {answer['duration']}\n\n"
    
    grammar_instruction = f"""
    {analysis_text}
    
    For each response, analyze the grammar quality and provide feedback.
    
    Provide your response in this EXACT JSON format:
    {{
        "responses": [
            {{
                "response_number": 1,
                "grammar_score": "Excellent/Good/Fair/Poor",
                "grammar_feedback": "Brief specific feedback about grammar (1-2 sentences)",
                "word_count": number_of_words_in_answer,
                "wpm": calculated_words_per_minute
            }},
            // ... repeat for each response
        ],
        "overall_assessment": {{
            "average_grammar": "Overall grammar level",
            "communication_clarity": "Assessment of overall communication",
            "language_proficiency": "Overall language proficiency level"
        }}
    }}
    """
    
    response = await call_gemini_api_async([], grammar_instruction)
    
    if response["success"]:
        try:
            # Try to parse JSON from response
            content = response["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                return analysis_data
        except Exception as e:
            print(f"Error parsing grammar analysis: {e}")
    
    # Fallback analysis
    fallback_responses = []
    for i, answer in enumerate(all_answers):
        duration_seconds = parse_duration_to_seconds(answer['duration'])
        wpm = calculate_wpm(answer['answer'], duration_seconds)
        fallback_responses.append({
            "response_number": i + 1,
            "grammar_score": "Fair",
            "grammar_feedback": "Grammar analysis completed",
            "word_count": len(answer['answer'].split()),
            "wpm": wpm
        })
    
    return {
        "responses": fallback_responses,
        "overall_assessment": {
            "average_grammar": "Fair",
            "communication_clarity": "Analysis completed",
            "language_proficiency": "Intermediate"
        }
    }

async def start_interview_logic(db: Session, session_id: str) -> Dict[str, Any]:
    """
    Async version of start interview logic
    """
    # Initialize conversation session
    conversation_sessions[session_id] = {
        "current_question_index": 0,
        "interview_context": [],
        "interview_completed": False,
        "all_answers": [],
        "current_step": "main_question",
        "interview_questions": [],
        "off_topic_attempts": 0  # Track off-topic attempts
    }

    # Ambil pertanyaan dari database
    questions_db = db.query(Materiinterview).order_by(Materiinterview.idmateriinterview).all()
    interview_questions = [q.question for q in questions_db]

    if not interview_questions:
        return {"error": "No interview questions found in database."}

    conversation_sessions[session_id]["interview_questions"] = interview_questions

    # Get the first question
    question = interview_questions[0]
    conversation_sessions[session_id]["interview_context"].append({"role": "assistant", "content": question})

    return {
        "topic": interview_topic,
        "question": question
    }

async def answer_question_logic(answer_data: Dict[str, str], session_id: str) -> Dict[str, Any]:
    """
    Updated answer question logic with off-topic detection
    """
    answer_text = answer_data.get("answer", "").strip()
    duration_str = answer_data.get("duration", "0:00")
    
    if not answer_text:
        return {"error": "Answer cannot be empty"}
    
    # Get session data
    session_data = conversation_sessions.get(session_id)
    if not session_data:
        return {"error": "Session not found. Please start interview first."}
    
    # Check if interview is already completed
    if session_data.get("interview_completed", False):
        conclusion_instruction = """
        You are a professional interviewer. The interview is now complete. 
        Provide a thoughtful, personalized concluding statement to the candidate.
        Be encouraging, professional, and specific about the value of their interview responses.
        Keep it concise and professional.
        """
        
        gemini_response = await call_gemini_api_async(
            session_data["interview_context"], 
            conclusion_instruction
        )
        
        if gemini_response["success"]:
            ai_conclusion = gemini_response["content"]
        else:
            ai_conclusion = "Thank you for completing this interview. Your responses demonstrate your experience and skills."
            
        return {
            "status": "completed", 
            "message": ai_conclusion,
            "interview_completed": True
        }

    # Get current question for relevance check
    current_step = session_data.get("current_step", "main_question")
    current_question_index = session_data["current_question_index"]
    
    if current_step == "main_question":
        current_question = session_data["interview_questions"][current_question_index]
    else:  # follow_up step
        current_question = session_data.get("current_followup_question", "Follow-up question")
    
    # Check answer relevance
    relevance_check = await check_answer_relevance(current_question, answer_text)
    
    # If answer is off-topic, ask the same question again
    if not relevance_check["is_relevant"]:
        session_data["off_topic_attempts"] = session_data.get("off_topic_attempts", 0) + 1
        
        # Generate appropriate off-topic response
        off_topic_instruction = f"""
        You are a professional interviewer. The candidate just gave an off-topic answer to your question.
        
        Original Question: "{current_question}"
        Candidate's Off-topic Answer: "{answer_text}"
        Reason it's off-topic: {relevance_check["reason"]}
        
        Politely redirect them back to the original question. Be professional and encouraging.
        
        Provide your response in this EXACT JSON format:
        {{
            "redirect_message": "Polite message explaining they should focus on the question",
            "repeated_question": "Repeat the exact same question"
        }}
        """
        
        gemini_response = await call_gemini_api_async([], off_topic_instruction)
        
        if gemini_response["success"]:
            try:
                content = gemini_response["content"]
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    redirect_message = response_data.get("redirect_message", "Please focus on the interview question.")
                    repeated_question = response_data.get("repeated_question", current_question)
                else:
                    raise Exception("No JSON found")
            except:
                redirect_message = "I'd like you to focus on the interview question I asked."
                repeated_question = current_question
        else:
            redirect_message = "Please focus on answering the interview question."
            repeated_question = current_question
        
        # Don't add off-topic answer to context, just add the redirect
        session_data["interview_context"].append({"role": "assistant", "content": f"{redirect_message} {repeated_question}"})
        
        print(f"Off-topic detected. Redirect: {redirect_message}")
        print(f"Repeating question: {repeated_question}")
        
        return {
            "status": "off_topic",
            "message": f"{redirect_message} {repeated_question}",
            "interview_completed": False,
            "off_topic_attempts": session_data["off_topic_attempts"]
        }
    
    # If answer is on-topic, proceed with normal flow
    # Reset off-topic attempts since we got a relevant answer
    session_data["off_topic_attempts"] = 0
    
    # Calculate WPM (grammar will be done in summary)
    duration_seconds = parse_duration_to_seconds(duration_str)
    wpm = calculate_wpm(answer_text, duration_seconds)
    
    # Add user's answer to context
    session_data["interview_context"].append({"role": "user", "content": answer_text})
    
    print(f"DEBUG: Current step: {current_step}, Question index: {current_question_index}")
    
    # Handle based on current step
    if current_step == "main_question":
        # This is the main question answer - generate follow-up
        current_question = session_data["interview_questions"][current_question_index]
        
        # Store main answer
        session_data["all_answers"].append({
            "question": current_question,
            "answer": answer_text,
            "duration": duration_str,
            "wpm": wpm,
            "is_followup": False
        })
        
        # Generate follow-up question
        followup_instruction = f"""
        You are a professional IT industry interviewer. 
        The candidate just answered: "{answer_text}"
        
        RULES:
        - First, provide brief constructive feedback about their answer (1-2 sentences)
        - Then ask ONE specific technical follow-up question related to their skills or experience
        - ONLY ask technical questions about specific skills, projects, or technologies they mentioned
        - Keep total response to 3-4 sentences maximum
        - Be professional and encouraging
        - The answer must be polite, culturally appropriate expressions instead of direct or blunt phrases (e.g., say "I've had enough" instead of "I'm full"). Give the feedback if the answer is impolite
        
        Provide your response in this EXACT JSON format:
        {{
            "feedback": "Your constructive feedback here",
            "followup_question": "Your specific follow-up question here"
        }}
        """

        gemini_response = await call_gemini_api_async(
            session_data["interview_context"], 
            followup_instruction
        )

        if gemini_response["success"]:
            try:
                response_content = gemini_response["content"]
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    feedback = response_data.get("feedback", "Thank you for your response.")
                    followup_question = response_data.get("followup_question", "Could you elaborate on that?")
                else:
                    raise Exception("No JSON found")
            except:
                feedback = "Thank you for sharing your experience."
                followup_question = "Could you describe a specific technical challenge you've encountered in your recent projects?"
        else:
            feedback = "Thank you for sharing your experience."
            followup_question = "Could you describe a specific technical challenge you've encountered in your recent projects?"
            
        print(f"AI feedback: {feedback}")
        print(f"AI follow-up question: {followup_question}")

        # Store follow-up question and update step
        session_data["current_followup_question"] = followup_question
        session_data["current_step"] = "follow_up"
        session_data["interview_context"].append({"role": "assistant", "content": followup_question})

        return {
            "status": "continue",
            "feedback": feedback,
            "message": followup_question,
            "interview_completed": False
        }
    
    elif current_step == "follow_up":
        # This is the follow-up answer - provide feedback and move to next question
        followup_question = session_data.get("current_followup_question", "Follow-up question")
        current_question = session_data["interview_questions"][current_question_index]
        
        # Store follow-up answer
        session_data["all_answers"].append({
            "question": followup_question,
            "answer": answer_text,
            "duration": duration_str,
            "wpm": wpm,
            "is_followup": True,
            "main_question": current_question
        })
        
        # Generate feedback for both answers
        feedback_instruction = """
        You are a professional IT industry interviewer. 
        The candidate has now answered both the main question and your follow-up question.
        
        RULES:
        - Provide thoughtful, constructive feedback on their responses
        - Be specific and professional
        - Keep your response to 2-4 sentences
        - Focus on their technical skills and experience
        - Sound encouraging but professional
        """

        gemini_response = await call_gemini_api_async(
            session_data["interview_context"], 
            feedback_instruction
        )

        if not gemini_response["success"]:
            ai_feedback = "Thank you for your detailed response. Your experience is valuable."
        else:
            ai_feedback = gemini_response["content"]
            
        print(f"AI feedback: {ai_feedback}")
        session_data["interview_context"].append({"role": "assistant", "content": ai_feedback})

        # Move to next question
        session_data["current_question_index"] += 1
        session_data["current_step"] = "main_question"  # Reset for next question
        
        # Check if there are more questions
        if session_data["current_question_index"] < len(session_data["interview_questions"]):
            next_question = session_data["interview_questions"][session_data["current_question_index"]]
            session_data["interview_context"].append({"role": "assistant", "content": next_question})
            
            return {
                "status": "continue",
                "feedback": ai_feedback,
                "message": next_question,
                "interview_completed": False
            }
        else:
            # No more questions - complete interview
            session_data["interview_completed"] = True
            
            # Get a proper conclusion from Gemini
            conclusion_instruction = """
            You are a professional interviewer. The interview is now complete. 
            Provide a thoughtful, personalized concluding statement to the candidate.
            Be encouraging, professional, and specific to their responses throughout the interview.
            Thank them for their time and mention that they will receive feedback.
            Make it short 1-2 simplified lines.
            """
            
            gemini_response = await call_gemini_api_async(
                session_data["interview_context"], 
            conclusion_instruction
            )
            
            if gemini_response["success"]:
                ai_conclusion = gemini_response["content"]
            else:
                ai_conclusion = "Thank you for completing this interview. Your responses demonstrate your experience and skills."
                
            print(f"AI conclusion: {ai_conclusion}")
            
            return {
                "status": "completed",
                "feedback": ai_feedback,
                "message": ai_conclusion,
                "interview_completed": True
            }

    return {"error": "Unexpected state in interview flow"}

async def get_interview_summary(db: Session, talent_id: int, session_id: str) -> Dict[str, Any]:
    """
    Async version with batch grammar analysis
    """
    session_data = conversation_sessions.get(session_id)
    
    if not session_data or not session_data.get("interview_completed", False):
        return {
            "success": False,
            "message": "Interview is not yet complete. Please finish the interview first."
        }

    if not session_data.get("all_answers"):
        return {
            "success": False,
            "message": "No interview data available."
        }

    # Perform batch grammar and WPM analysis
    analysis_result = await analyze_grammar_and_wpm_batch(session_data["all_answers"])
    
    # Update answers with grammar analysis
    if "responses" in analysis_result:
        for i, response_analysis in enumerate(analysis_result["responses"]):
            if i < len(session_data["all_answers"]):
                session_data["all_answers"][i].update({
                    "grammar_score": response_analysis.get("grammar_score", "Fair"),
                    "grammar_feedback": response_analysis.get("grammar_feedback", ""),
                    "wpm": response_analysis.get("wpm", session_data["all_answers"][i].get("wpm", 0))
                })

    # Calculate overall statistics
    total_answers = len(session_data["all_answers"])
    total_wpm = sum([ans.get("wpm", 0) for ans in session_data["all_answers"]])
    avg_wpm = round(total_wpm / total_answers, 1) if total_answers > 0 else 0
    
    # Grammar analysis
    grammar_scores = [ans.get("grammar_score", "Fair") for ans in session_data["all_answers"]]
    grammar_counts = {score: grammar_scores.count(score) for score in set(grammar_scores)}
    
    # Organize answers by main question
    organized_answers = {}
    for item in session_data["all_answers"]:
        if item.get("is_followup", False):
            main_q = item.get("main_question", "Unknown question")
            if main_q not in organized_answers:
                organized_answers[main_q] = {"main_answer": "", "followup_answer": "", "main_analysis": {}, "followup_analysis": {}}
            organized_answers[main_q]["followup_answer"] = item["answer"]
            organized_answers[main_q]["followup_question"] = item["question"]
            organized_answers[main_q]["followup_analysis"] = {
                "wpm": item.get("wpm", 0),
                "grammar_score": item.get("grammar_score", "Fair"),
                "grammar_feedback": item.get("grammar_feedback", "")
            }
        else:
            q = item["question"]
            if q not in organized_answers:
                organized_answers[q] = {"main_answer": "", "followup_answer": "", "main_analysis": {}, "followup_analysis": {}}
            organized_answers[q]["main_answer"] = item["answer"]
            organized_answers[q]["main_analysis"] = {
                "wpm": item.get("wpm", 0),
                "grammar_score": item.get("grammar_score", "Fair"),
                "grammar_feedback": item.get("grammar_feedback", "")
            }

    # Build summary context
    summary_context = []

    # Add statistics and each Q&A pair to context
    stats_context = f"""
    INTERVIEW STATISTICS:
    - Total Questions Answered: {total_answers}
    - Average WPM: {avg_wpm}
    - Grammar Score Distribution: {grammar_counts}
    - Overall Grammar Assessment: {analysis_result.get('overall_assessment', {}).get('average_grammar', 'Fair')}
    
    DETAILED Q&A ANALYSIS:
    """
    
    for question, answers in organized_answers.items():
        context_text = f"""
        Main Question: {question}
        Main Answer: {answers['main_answer']}
        Main Answer WPM: {answers['main_analysis'].get('wpm', 0)}
        Main Answer Grammar: {answers['main_analysis'].get('grammar_score', 'Fair')}
        
        Follow-up Question: {answers.get('followup_question', 'N/A')}
        Follow-up Answer: {answers.get('followup_answer', 'N/A')}
        Follow-up WPM: {answers['followup_analysis'].get('wpm', 0)}
        Follow-up Grammar: {answers['followup_analysis'].get('grammar_score', 'Fair')}
        """
        stats_context += context_text + "\n"
    
    summary_context.append({"role": "user", "content": stats_context})

    # Summary instruction for Gemini
    summary_instruction = """
    You are a professional IT interviewer providing comprehensive feedback after an interview.
    
    Analyze the candidate's interview responses including their WPM (words per minute) performance and grammar usage.
    
    Provide your analysis in this EXACT JSON format:
    {
        "summary": {
            "strengths": [
                "Specific strength 1 based on their technical answers and performance",
                "Specific strength 2 including communication speed or grammar if notable",
                "Specific strength 3 referencing their actual responses"
            ],
            "weaknesses": [
                "Specific area for improvement 1 based on technical responses",
                "Specific area for improvement 2 including WPM or grammar concerns if relevant",
                "Specific area for improvement 3 with constructive feedback"
            ],
            "overall_performance": {
                "technical_knowledge": "Excellent/Good/Fair/Poor with brief explanation",
                "communication_speed": "Assessment based on WPM performance",
                "grammar_usage": "Assessment based on grammar scores",
                "recommendation": "Brief overall recommendation"
            }
        }
    }
    
    Keep each point to 1-2 sentences. Be professional, constructive, and specific to their actual answers.
    Focus on technical skills, communication clarity, response speed, and language proficiency.
    """

    gemini_response = await call_gemini_api_async(summary_context, summary_instruction)

    if not gemini_response["success"]:
        return {
            "success": False,
            "error": "Failed to get summary from Gemini", 
            "detail": gemini_response.get("error", "Unknown error")
        }
    
    try:
        # Try to parse JSON from response
        summary_content = gemini_response["content"]
        json_match = re.search(r'\{.*\}', summary_content, re.DOTALL)
        if json_match:
            summary_data = json.loads(json_match.group())
            return {
                "success": True,
                "summary": summary_data,
                "statistics": {
                    "total_answers": total_answers,
                    "average_wpm": avg_wpm,
                    "grammar_distribution": grammar_counts,
                    "overall_grammar_assessment": analysis_result.get('overall_assessment', {})
                }
            }
    except Exception as e:
        print(f"JSON parsing error: {e}")
    
    # Fallback if JSON parsing fails
    return {
        "success": True,
        "summary": {
            "summary": {
                "strengths": ["Completed the interview successfully"],
                "weaknesses": ["Areas for improvement to be assessed"],
                "overall_performance": {
                    "technical_knowledge": "Assessment completed",
                    "communication_speed": f"Average WPM: {avg_wpm}",
                    "grammar_usage": "Grammar analysis completed",
                    "recommendation": "Continue developing technical and communication skills"
                }
            }
        },
        "statistics": {
            "total_answers": total_answers,
            "average_wpm": avg_wpm,
            "grammar_distribution": grammar_counts,
            "overall_grammar_assessment": analysis_result.get('overall_assessment', {})
        }
    }

async def save_interview_summary(db: Session, idtalent: int, summary_data: Dict[str, Any], statistics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async version of save interview summary
    """
    try:
        # Extract data directly from the parameters
        summary_content = summary_data.get("summary", {})

        # Extract strengths and weaknesses as readable text
        strengths = summary_content.get("strengths", [])
        weaknesses = summary_content.get("weaknesses", [])
        overall_performance = summary_content.get("overall_performance", {})

        # Format strengths and weaknesses as readable text
        strengths_text = "\n".join([f"• {strength}" for strength in strengths])
        weaknesses_text = "\n".join([f"• {weakness}" for weakness in weaknesses])

        # Create detailed feedback text
        feedback_text = f"""INTERVIEW FEEDBACK SUMMARY

STRENGTHS:
{strengths_text}

AREAS FOR IMPROVEMENT:
{weaknesses_text}

OVERALL PERFORMANCE:
• Technical Knowledge: {overall_performance.get('technical_knowledge', 'N/A')}
• Communication Speed: {overall_performance.get('communication_speed', 'N/A')}
• Grammar Usage: {overall_performance.get('grammar_usage', 'N/A')}
• Recommendation: {overall_performance.get('recommendation', 'N/A')}

INTERVIEW STATISTICS:
• Total Answers: {statistics.get('total_answers', 0)}
• Average WPM: {statistics.get('average_wpm', 0)}
• Grammar Distribution: {statistics.get('grammar_distribution', {})}
• Overall Grammar: {statistics.get('overall_grammar_assessment', {}).get('average_grammar', 'N/A')}
"""
        
        # Get average WPM and dominant grammar score
        avg_wpm = statistics.get('average_wpm', 0)
        
        # Determine most common grammar score
        grammar_dist = statistics.get('grammar_distribution', {})
        dominant_grammar = max(grammar_dist, key=grammar_dist.get) if grammar_dist else 'Fair'
        
        # Create a new instance of Hasillatihaninterview
        new_summary = Hasillatihaninterview(
            idtalent=idtalent,
            waktulatihan=datetime.now(),
            feedback=feedback_text,  # Save as formatted readable text
            wpm=avg_wpm,
            grammar=dominant_grammar
        )
        
        # Add and commit the new summary to the database
        db.add(new_summary)
        db.commit()
        db.refresh(new_summary)
        
        return {
            "success": True, 
            "message": "Summary saved successfully.",
            "id": new_summary.idhasilinterview,
            "saved_data": {
                "feedback_preview": feedback_text[:200] + "..." if len(feedback_text) > 200 else feedback_text,
                "wpm": avg_wpm,
                "grammar": dominant_grammar
            }
        }
        
    except Exception as e:
        print(f"Error saving interview summary: {e}")
        return {
            "success": False,
            "message": f"Failed to save summary: {str(e)}"
        }