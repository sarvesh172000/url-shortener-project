# This file will hold all our functions for interacting with the database (Create, Read, Update, Delete).
# backend/crud.py
from sqlalchemy.orm import Session
import secrets

from . import models, schemas

def get_db_url_by_key(db: Session, url_key: str) -> models.URL:
    """Return a URL object from the database if the key is found."""
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )

def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    """Return a URL object from the database if the secret_key is found."""
    return (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active)
        .first()
    )

def create_db_url(db: Session, url: schemas.URLBase) -> models.URL:
    """Create a new URL in the database."""
    key = secrets.token_urlsafe(5)
    secret_key = f"{key}_{secrets.token_urlsafe(8)}"
    db_url = models.URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def update_db_clicks(db: Session, db_url: schemas.URL) -> models.URL:
    """Update the click count for a URL in the database."""
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url
