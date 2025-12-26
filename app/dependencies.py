from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import database, crud, models, auth

def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    # 1. Récupération du cookie
    token = request.cookies.get("access_token")
    
    # DEBUG: On affiche ce qu'on trouve
    if not token:
        print("🛑 DEBUG: Aucun cookie 'access_token' reçu du navigateur.")
        return None
    
    # 2. Nettoyage (Au cas où le mot 'Bearer ' traîne encore, on l'enlève)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
        
    try:
        # 3. Décodage
        # On print la clé secrète (juste les 3 premiers caractères pour vérifier qu'elle existe)
        print(f"ℹ️ DEBUG: Vérification avec Secret Key commençant par: {auth.SECRET_KEY[:3]}...")
        
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            print("🛑 DEBUG: Token décodé mais pas de username (sub).")
            return None
            
    except JWTError as e:
        print(f"🛑 DEBUG: Erreur de décodage JWT : {e}")
        return None

    # 4. Recherche en DB
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        print(f"🛑 DEBUG: Username '{username}' introuvable en base de données.")
        return None

    print(f"✅ DEBUG: Utilisateur '{username}' connecté avec succès !")
    return user

def require_user(user: models.User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"},
            detail="Not authenticated"
        )
    return user