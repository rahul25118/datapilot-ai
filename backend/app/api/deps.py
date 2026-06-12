import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from uuid import UUID
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
JWT_SECRET = os.getenv("JWT_SECRET", "4f923c8a901dcefe2c1a84f30dcb9071c320a4b0821e23364f7b494101bc3d5c")
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate infrastructure security authentication token metrics.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
