from pydantic import BaseModel

class ChatInput(BaseModel):
    user_input: str
    duration: str

class ChatResponse(BaseModel):
    response: str
    confidence_score: int
    grammar_check: str