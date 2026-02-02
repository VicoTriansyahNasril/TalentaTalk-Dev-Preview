from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseBase(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None