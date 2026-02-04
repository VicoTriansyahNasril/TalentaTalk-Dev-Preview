from pydantic import BaseModel
from typing import List, Optional

class Topic(BaseModel):
    id: int
    title: str
    description: str

class TopicListResponse(BaseModel):
    topics: List[Topic]

class ChatInput(BaseModel):
    user_input: str
    duration: str
    topic_id: Optional[int] = 1 

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