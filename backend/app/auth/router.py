from datetime import datetime, timedelta
from typing import Dict

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
import jwt

from ..config import settings
from ..models import Token, UserCreate, UserLogin

# Simple in-memory store for demo purposes
USERS: Dict[str, Dict] = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


def create_access_token(data: Dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user (demo implementation)."""
    if user.username in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    USERS[user.username] = {
        "username": user.username,
        "password": pwd_context.hash(user.password),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token({"sub": user.username, "role": user.role})
    return Token(access_token=access_token, token_type="bearer", user_role=user.role)


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Authenticate user and return JWT."""
    stored = USERS.get(user.username)
    if not stored or not pwd_context.verify(user.password, stored["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username, "role": stored["role"]})
    return Token(access_token=access_token, token_type="bearer", user_role=stored["role"])
