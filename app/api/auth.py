# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.api.schemas import UserCreate, UserLogin, UserResponse, LoginResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SIGNUP
@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    new_user = User(
        fullname=data.fullname,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# LOGIN
@router.post("/login", response_model=LoginResponse, status_code=200)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    response = JSONResponse(
        content={
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email
            }
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60*60*24
    )

    return response

# LOGOUT
@router.post("/logout")
def logout(current_user : User = Depends(get_current_user)):
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax"
    )
    return response

