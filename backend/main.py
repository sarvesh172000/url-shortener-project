# backend/main.py
import pathlib
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import redis

# Import SlowAPI components
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from . import models, schemas, crud
from .database import SessionLocal, engine

# Set up the rate limiter
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# Add the exception handler for rate limit exceeded errors
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten", response_model=schemas.URLInfo)
@limiter.limit("5/minute")
def create_url(request: Request, url: schemas.URLBase, db: Session = Depends(get_db)):
    db_url = crud.create_db_url(db=db, url=url)
    base_url = "http://127.0.0.1:8000"
    # Construct a Pydantic model for the response to ensure correct serialization
    response_data = schemas.URLInfo(
        target_url=db_url.target_url,
        is_active=db_url.is_active,
        clicks=db_url.clicks,
        url=f"{base_url}/{db_url.key}",
        admin_url=f"{base_url}/admin/{db_url.secret_key}"
    )
    return response_data

@app.get("/{url_key}")
def forward_to_target_url(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db)
):
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    cached_url = r.get(url_key)

    if cached_url:
        # If URL is in cache, redirect quickly and update clicks
        db_url_for_clicks = crud.get_db_url_by_key(db, url_key=url_key)
        if db_url_for_clicks:
            crud.update_db_clicks(db=db, db_url=db_url_for_clicks)
        return RedirectResponse(cached_url)
    else:
        # If not in cache, get from DB
        db_url = crud.get_db_url_by_key(db, url_key=url_key)
        if db_url:
            # Add to cache for next time
            r.set(url_key, db_url.target_url)
            crud.update_db_clicks(db=db, db_url=db_url)
            return RedirectResponse(db_url.target_url)
        else:
            raise HTTPException(status_code=404, detail="URL not found")

@app.get("/admin/{secret_key}", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    db_url = crud.get_db_url_by_secret_key(db, secret_key=secret_key)
    if db_url:
        base_url = "http://127.0.0.1:8000"
        # Construct a Pydantic model for the response
        response_data = schemas.URLInfo(
            target_url=db_url.target_url,
            is_active=db_url.is_active,
            clicks=db_url.clicks,
            url=f"{base_url}/{db_url.key}",
            admin_url=f"{base_url}/admin/{db_url.secret_key}"
        )
        return response_data
    else:
        raise HTTPException(status_code=404, detail="URL not found")

# --- ROBUST STATIC FILE SERVING ---
# Get the path to the directory where main.py is located
backend_dir = pathlib.Path(__file__).resolve().parent
# Get the path to the root project directory (one level up)
root_dir = backend_dir.parent
# Define the path to the frontend directory
frontend_dir = root_dir / "frontend"

# Mount the frontend directory using the absolute path
# This MUST come after all your API routes
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="static")