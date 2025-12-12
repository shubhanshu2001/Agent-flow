from fastapi import FastAPI
from app.db.session import engine, Base
from app.models import User
from contextlib import asynccontextmanager

from fastapi import Depends
from app.api.deps import get_current_user

from app.api.auth import router as auth_router
from app.api.session_routes import router as session_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Agentic Workflow Companion", lifespan=lifespan)


# routes
app.include_router(auth_router)
app.include_router(session_router)

@app.get("/me")
def get_me(user : User = Depends(get_current_user)):
    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
