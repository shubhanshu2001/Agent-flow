# app/api/deps.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def extract_token(request: Request) -> str | None:
    """
    Priority:
    1. access_token cookie
    2. Authorization header token
    """
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    # fallback: header-based token
    try:
        header_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
        if header_token:
            return header_token
    except:
        pass

    return None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = extract_token(request)

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user from DB
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
