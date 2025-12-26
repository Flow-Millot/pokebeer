from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from .. import database, crud, auth

router = APIRouter()

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    crud.create_user(db, username, auth.get_password_hash(password))
    return RedirectResponse(url="/login", status_code=303)

@router.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        # On garde le RedirectResponse ici aussi
        return RedirectResponse(url="/login?error=Invalid Credentials", status_code=303)
    
    access_token = auth.create_access_token(data={"sub": user.username})
    
    # Création de la réponse de redirection
    response = RedirectResponse(url="/", status_code=303)
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return response

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response