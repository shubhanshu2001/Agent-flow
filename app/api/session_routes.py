# app/api/session_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.message import Message
from app.api.schemas_session import (
    SessionCreate, SessionResponse, SessionDetail,
    MessageCreate, MessageResponse
)

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
@router.post("/{session_id}/messages", response_model=MessageResponse)
def send_message(session_id: int, payload: MessageCreate, db: Session = Depends(get_db), user : User = Depends(get_current_user)):
    
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(404, "Session not found")

    # Store user message
    new_message = Message(
        session_id=session_id,
        sender="user",
        content=payload.content,
        meta=None
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message
