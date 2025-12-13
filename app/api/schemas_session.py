# app/api/schemas_session.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    sender: str
    content: str
    meta: Optional[dict]
    created_at: datetime

    class Config:
        orm_mode = True

class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse

    class Config:
        orm_mode = True


class SessionCreate(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    title: Optional[str]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class SessionDetail(BaseModel):
    id: int
    title: Optional[str]
    status: str
    messages: List[MessageResponse]

    class Config:
        orm_mode = True
