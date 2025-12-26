from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import database, crud, models, auth # Assurez-vous d'importer votre module auth qui contient SECRET_KEY

# Fonction utilitaire pour récupérer le token depuis le cookie
def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token") # Le nom donné dans set_cookie
    if not token:
        return None
    # Dans auth.py, vous avez mis "Bearer " devant, il faut peut-être l'enlever
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    return token

def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    token = get_token_from_cookie(request)
    if not token:
        return None # Retourne None si pas de cookie (l'utilisateur est anonyme)

    try:
        # Décodage du token
        # ATTENTION : Remplacez auth.SECRET_KEY et auth.ALGORITHM par vos vraies variables
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        return None
    return user

# Dépendance stricte (pour les pages qui nécessitent absolument d'être connecté)
def require_user(user: models.User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"}, # Redirige vers login si pas connecté
            detail="Not authenticated"
        )
    return user