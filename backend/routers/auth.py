from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import secrets

from backend.utils.database import get_db
from backend.utils.auth import create_access_token
from backend.schemas.schemas import UserCreate, UserResponse, GoogleOAuthRequest, TokenRefreshResponse
from backend.models.models import User
from backend.services.google_fit_service import GoogleFitService
from backend.config import GOOGLE_REDIRECT_URI

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/google", response_model=UserResponse)
async def google_login(request: GoogleOAuthRequest, db: Session = Depends(get_db)):
    tokens = GoogleFitService.exchange_code_for_tokens(request.code, GOOGLE_REDIRECT_URI)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code for tokens"
        )
    
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")
    
    import requests
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if userinfo_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from Google"
        )
    
    userinfo = userinfo_response.json()
    google_id = userinfo["id"]
    email = userinfo["email"]
    name = userinfo.get("name", "")
    
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if not user:
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            user.google_id = google_id
            user.google_access_token = access_token
            user.google_refresh_token = refresh_token
            user.last_login = datetime.utcnow()
        else:
            user = User(
                name=name,
                email=email,
                google_id=google_id,
                google_access_token=access_token,
                google_refresh_token=refresh_token,
                last_login=datetime.utcnow()
            )
            db.add(user)
    else:
        user.google_access_token = access_token
        user.google_refresh_token = refresh_token
        user.last_login = datetime.utcnow()
        if name:
            user.name = name
    
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.google_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or no refresh token"
        )
    
    google_service = GoogleFitService(
        access_token=user.google_access_token or "",
        refresh_token=user.google_refresh_token
    )
    
    if not google_service.refresh_access_token():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh access token"
        )
    
    user.google_access_token = google_service.access_token
    db.commit()
    
    return TokenRefreshResponse(access_token=google_service.access_token)

@router.post("/logout")
async def logout(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.google_access_token = None
    user.google_refresh_token = None
    db.commit()
    
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/google/url")
async def get_google_auth_url():
    state = secrets.token_urlsafe(32)
    url = GoogleFitService.get_authorization_url(state, GOOGLE_REDIRECT_URI)
    return {"url": url, "state": state}

@router.post("/demo", response_model=UserResponse)
async def demo_login(db: Session = Depends(get_db)):
    email = "demo@example.com"
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            name="Demo User",
            email=email,
            last_login=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
    return user

