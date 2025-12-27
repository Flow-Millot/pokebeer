import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from openai import OpenAI  # Modification : Utilisation du client OpenAI
from .. import database, models

router = APIRouter(
    prefix="/api",
    tags=["Chatbot"]
)

HF_TOKEN = os.getenv("HF_TOKEN_READ")

# On initialise le client selon la méthode de la documentation (Inference Providers)
# L'URL du routeur permet d'unifier l'accès aux différents fournisseurs d'inférence.
if HF_TOKEN:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN
    )
else:
    client = None

# Modèle choisi
MODEL_ID = "moonshotai/Kimi-K2-Instruct-0905"

class ChatRequest(BaseModel):
    message: str

def format_beers_context(db: Session):
    """Formate la liste des bières pour le contexte du chatbot"""
    beers = db.query(models.Beer).limit(50).all()
    if not beers:
        return None
    context_list = []
    for b in beers:
        style = b.style if hasattr(b, "style") and b.style else "Style inconnu"
        desc = b.description if hasattr(b, "description") and b.description else "Pas de description"
        line = f"- {b.name} ({b.brewery}) | Style: {style} | {desc}"
        context_list.append(line)
    return "\n".join(context_list)

@router.post("/chat")
def chat_endpoint(request: ChatRequest, db: Session = Depends(database.get_db)):
    if not client:
        raise HTTPException(status_code=500, detail="Token HF manquant.")

    beers_context = format_beers_context(db) or "Aucune bière en stock."

    messages = [
        {
            "role": "system",
            "content": f"""Tu es un sommelier bière expert.
            Ton stock est LIMITÉ à cette liste :
            {beers_context}
            
            Consignes :
            - Ne recommande QUE des bières de cette liste.
            - Si on te demande une bière hors liste, dis poliment qu'elle n'est pas en stock.
            - Réponds en français."""
        },
        {
            "role": "user", 
            "content": request.message
        }
    ]

    try:
        # 2. Appel via la méthode compatible OpenAI
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=False
        )

        # 3. Extraction de la réponse
        return {"response": response.choices[0].message.content}

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur API : {error_msg}")
        
        # Note: Avec le routeur, les erreurs de 'loading' (cold start) peuvent être moins fréquentes 
        # ou renvoyées sous forme de code 503, mais on garde la logique au cas où.
        if "loading" in error_msg.lower():
             return {"response": "Le sommelier arrive (Modèle en chargement)... Réessayez dans 30 secondes."}
        
        return {"response": "Désolé, une erreur technique est survenue."}