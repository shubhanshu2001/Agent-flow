# app/api/session_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.message import Message
from app.api.schemas_session import (
    SessionCreate, SessionResponse, SessionDetail,
    MessageCreate, MessageResponse, SendMessageResponse
)
from app.services.llm_service import generate_llm_response
from app.services.agent_service import run_multi_agent


router = APIRouter(prefix="/sessions", tags=["Sessions"])

# create session
@router.post("/", response_model=SessionResponse)
def create_session(payload: SessionCreate, db: Session = Depends(get_db), user : User = Depends(get_current_user)):
    
    new_session = SessionModel(
        user_id=user.id,
        title=payload.title or "New Session"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session

# get user sessions
@router.get("/", response_model=list[SessionResponse])
def get_user_sessions(db: Session = Depends(get_db), user : User = Depends(get_current_user)):
    
    sessions = db.query(SessionModel)\
                 .filter(SessionModel.user_id == user.id)\
                 .order_by(SessionModel.created_at.desc())\
                 .all()
    
    return sessions

# get session details
@router.get("/{session_id}", response_model=SessionDetail)
def get_session_details(session_id: int, db: Session = Depends(get_db), user : User = Depends(get_current_user)):
    
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(404, "Session not found")

    return session

# send new message
@router.post("/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(session_id: int, payload: MessageCreate, db: Session = Depends(get_db), user : User = Depends(get_current_user)):

    """
    Stores the user message, generates an assistant response,
    stores the assistant message, and returns both.
    """
    
    # 1. Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(404, "Session not found")

    # 2. Store user message
    user_msg = Message(
        session_id=session_id,
        sender="user",
        content=payload.content,
        meta=None
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 3. Build full conversation history for LLM
    db_messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at.asc()).all()

    conversation = [
        {
            "role": "user" if m.sender == "user" else "assistant",
            "content": m.content
        }
        for m in db_messages
    ]

    # # 4. Generate assistant response via LLM
    # assistant_reply = await generate_llm_response(conversation)

    # 4. Generate assistant response via running multi agent workflow
    assistant_reply = run_multi_agent(conversation)

    # 5. Store assistant message in DB
    assistant_msg = Message(
        session_id=session_id,
        sender="assistant",
        content=assistant_reply,
        meta=None
    )

    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # 6. Return both messages for frontend convenience
    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg
    }
