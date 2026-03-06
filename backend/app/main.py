import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, twitter, posts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SocialMedia Web", version="1.0.0")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(twitter.router)
app.include_router(posts.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
