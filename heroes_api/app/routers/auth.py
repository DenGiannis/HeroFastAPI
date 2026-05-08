# Authentication routes and logic
# POST /auth/register (Public) - Register a new user
# POST /auth/login (Public) - Login and return access token and token type
# GET /auth/me (Authenticated) - Get current user info

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.security import hash_password, verify_password, create_access_token
from app.db import get_session
from app.models import User
from app.dependencies import SessionDependency, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_session)):
    """Register a new user."""
    user = db.exec(select(User).where(User.username == request.username)).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = hash_password(request.password)
    new_user = User(username=request.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDependency
):
    """
    OAuth2 password flow login.
    Validates credentials and returns {access_token, token_type}.
    Use the Swagger "Authorize" button to try it interactively.
    """
    user = session.exec(select(User).where(User.username == form.username)).first()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
    }

@router.get("/me")
def get_current_user(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user

