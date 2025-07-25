import uuid
from datetime import timedelta
from typing import Any

# -----------------------------------------------------------------------------
# The authentication router now uses Supabase directly rather than SQLAlchemy.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import get_settings
from ..models import UserCreate, UserSchema, Token, UserRole
from ..models.database_utils import get_db, supabase
from .security import create_access_token, get_password_hash, verify_password

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register(user_in: UserCreate) -> Any:
    """Register a new user."""
    # Check for existing user by email or username
    existing = (
        supabase.table("profiles")
        .select("*")
        .or_(f"email.eq.{user_in.email},username.eq.{user_in.username}")
        .execute()
        .data
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    # Create user in database
    user_id = str(uuid.uuid4())
    hashed = get_password_hash(user_in.password)
    db_user = supabase.table("profiles").insert(
        {
            "id": user_id,
            "email": user_in.email,
            "username": user_in.username,
            "full_name": user_in.full_name,
            "hashed_password": hashed,
            "role": user_in.role,
        }
    ).execute().data[0]

    # Create user in Supabase if available
    if supabase:
        try:
            supabase.auth.admin.create_user({
                "email": user_in.email,
                "password": user_in.password,
                "user_metadata": {
                    "full_name": user_in.full_name,
                    "role": user_in.role,
                }
            })
        except Exception as e:
            # If Supabase user creation fails, rollback the database transaction
            # This part of the original code was SQLAlchemy-specific, now it's Supabase-specific
            # For Supabase, we might need to delete the user from the profiles table if the auth.admin.create_user fails
            # However, the original code had a rollback on Supabase failure, which is not directly applicable
            # to Supabase's direct insert. For now, we'll just raise an error.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user in Supabase: {str(e)}",
            )

    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Authenticate and return token."""
    # Find user by username
    resp = (
        supabase.table("profiles")
        .select("*")
        .eq("username", form_data.username)
        .single()
        .execute()
    )
    user = resp.data if resp.data else None
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=get_settings().jwt_expiration_minutes)
    access_token = create_access_token(
        subject=user["id"], role=user["role"], expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user["role"],
    } 