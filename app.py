from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS: allow your GitHub Pages origin (edit ORIGINS before deploying)
ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "https://<your-github-username>.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Secret injected via HF Space Secrets (set by GitHub Actions)
MY_API_KEY = os.getenv("PUSHOVER_API_KEY")

@app.get("/")
def root():
    # Optional: serve this if you open the Space directly
    return FileResponse("index.html") if os.path.exists("index.html") else JSONResponse({"ok": True, "service": "hf-backend"})

@app.get("/hello")
def hello(name: str = "World"):
    if not MY_API_KEY:
        return JSONResponse({"error": "API key not set in Space Secrets"}, status_code=500)
    # Don't expose the key—only prove the server has it.
    return {"message": f"Hello {name}! ✅ Backend has a secret securely.", "service": "hf-backend"}
