# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat_routes import router as chat_router
from api.repo_routes import router as repo_router


app = FastAPI(title="AI Codebase Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",   # Vite default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

app.include_router(chat_router, prefix="/chat")
app.include_router(repo_router, prefix="/repo")

@app.get("/")
def health():
    return {"status": "ok"}