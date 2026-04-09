from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserOut
from app.utils.response import api_response

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> dict:
    """Register a new user and return an access token."""
    try:
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = User(email=payload.email, hashed_password=hash_password(payload.password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        token = create_access_token(str(user.id))
        return api_response(
            True,
            {"access_token": token, "token_type": "bearer", "user": UserOut.model_validate(user).model_dump(mode="json")},
            "User registered successfully",
            None,
        )
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login")
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> dict:
    """Authenticate a user and return a new access token."""
    try:
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        token = create_access_token(str(user.id))
        return api_response(
            True,
            {"access_token": token, "token_type": "bearer", "user": UserOut.model_validate(user).model_dump(mode="json")},
            "Login successful",
            None,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)) -> dict:
    """Return the currently authenticated user's profile."""
    try:
        return api_response(True, UserOut.model_validate(current_user).model_dump(mode="json"), "User profile loaded", None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
