from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import get_db
from . import auth, models

# Helper to get user from Cookie (since we are doing Frontend)
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
        
    user = db.query(models.User).filter(models.User.username == username).first()
    return user

# Enforce login for certain routes
def require_user(user: models.User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user