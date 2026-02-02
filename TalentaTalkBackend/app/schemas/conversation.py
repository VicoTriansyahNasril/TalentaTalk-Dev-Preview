from pydantic import BaseModel
from typing import List, Optional

class ChatInput(BaseModel):
    user_input: str
    duration: str

class ChatResponse(BaseModel):
    response: str
    confidence_score: int
    grammar_check: str

class ConversationStart(BaseModel):
    topic: str
    initial_question: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ConversationHistory(BaseModel):
    session_id: str
    topic: str
    history: List[ChatMessage]