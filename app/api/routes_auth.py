from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from influencer_agent.app.db.session import SessionLocal
from influencer_agent.app.models.user import User
from influencer_agent.app.models.instagram_account import InstagramAccount
from influencer_agent.app.core.config import settings
from influencer_agent.app.core.security import get_password_hash, verify_password
from influencer_agent.app.schemas.auth import UserCreate, UserLogin # Assuming schemas/auth.py is populated

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates the main user with a HASHED password.
    """
    # 1. Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create User with HASHED password
    hashed_pw = get_password_hash(user.password)
    
    db_user = User(
        email=user.email, 
        hashed_password=hashed_pw,
        full_name=user.full_name # Should be valid via UserCreate schema
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 3. Auto-link the Instagram Account from .env
    existing_account = db.query(InstagramAccount).filter(InstagramAccount.instagram_id == settings.INSTAGRAM_ACCOUNT_ID).first()
    
    if not existing_account:
        db_account = InstagramAccount(
            user_id=db_user.id,
            instagram_id=settings.INSTAGRAM_ACCOUNT_ID,
            access_token=settings.INSTAGRAM_ACCESS_TOKEN,
            username="Linked from Env"
        )
        db.add(db_account)
        db.commit()
    
    return {"message": "Registration Successful", "user_id": db_user.id, "email": db_user.email}

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates the user and returns success.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    return {"message": "Login Successful", "user_id": user.id, "email": user.email}