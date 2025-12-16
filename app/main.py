from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from app.models import User
from contextlib import asynccontextmanager

from app.api.auth import router as auth_router
from app.api.session_routes import router as session_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Agentic Workflow Companion", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "https://agentflow-sy.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(auth_router)
app.include_router(session_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
