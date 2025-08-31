
import logging
logger = logging.getLogger("uvicorn.error")

# app.py
import os
from urllib.parse import urlparse


from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- Config ---
ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip().rstrip("/") for o in ORIGINS_RAW.split(",") if o.strip()]
ALLOWED_HOSTS = {urlparse(o).netloc for o in ALLOWED_ORIGINS}

FRONTEND_APP_KEY = os.getenv("FRONTEND_APP_KEY", "")  # set as HF Space Secret
# Optional: other secrets you already use
BACKEND_INTERNAL_SECRET = os.getenv("PUSHOVER_API_KEY", "")

# --- CORS (browser preflight only) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],   # later: ["POST","OPTIONS"]
    allow_headers=["*"],
)

async def require_frontend(request: Request):
    """
    Enforce:
      - X-App-Key header matches FRONTEND_APP_KEY
      - Origin/Referer host is in allowlist (blocks address-bar & hotlinking)
      - No Origin/Referer => reject
    """
    if not FRONTEND_APP_KEY:
        raise HTTPException(status_code=500, detail="Server missing FRONTEND_APP_KEY")

    app_key = request.headers.get("x-app-key")
    if app_key != FRONTEND_APP_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    host_ok = False
    if origin:
        host_ok = urlparse(origin).netloc in ALLOWED_HOSTS
    elif referer:
        host_ok = urlparse(referer).netloc in ALLOWED_HOSTS

    if not host_ok:
        raise HTTPException(status_code=403, detail="Origin not allowed")

    return True

@app.get("/")
def root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return JSONResponse({"ok": True, "service": "hf-backend"})

@app.get("/hello", dependencies=[Depends(require_frontend)])
def hello_get(name: str = "World"):
    if not BACKEND_INTERNAL_SECRET:
        return JSONResponse({"error": "Internal secret not configured"}, status_code=500)
    return {"message": f"Hello {name}! Backend is configured.", "service": "hf-backend"}

@app.post("/hello", dependencies=[Depends(require_frontend)])
async def hello_post(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    name = (data.get("name") if isinstance(data, dict) else None) or "World"
    return {"message": f"Hello {name}! (POST)", "service": "hf-backend"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/_diag")
def diag():
    return {
        "has_FRONTEND_APP_KEY": bool(os.getenv("FRONTEND_APP_KEY")),
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", ""),
    }

@app.on_event("startup")
def _startup():
    has_key = bool(os.getenv("FRONTEND_APP_KEY"))
    logger.info("Startup: FRONTEND_APP_KEY=%s", "present" if has_key else "MISSING")
    logger.info("Startup: ALLOWED_ORIGINS=%s", os.getenv("ALLOWED_ORIGINS", "(none)"))