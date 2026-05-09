from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from config import get_settings
from db import get_session
from models import User

settings = get_settings()
SessionDependency = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDependency) -> User:
    """Decode the JWT token, search for the user and return or raise 401."""
    cred_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise cred_exception
    except JWTError:
        raise cred_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise cred_exception
    return user

def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Check if the user is admin and return or raise 403."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user