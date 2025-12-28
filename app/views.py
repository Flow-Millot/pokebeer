from django.shortcuts import render
from django.db.models import Avg, Q
from django.utils import timezone

from .models import Beer, Drinks

import os
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from openai import OpenAI

# Configuration du client AI (Une seule fois au chargement)
HF_TOKEN = os.getenv("HF_TOKEN_READ")
MODEL_ID = "moonshotai/Kimi-K2-Instruct-0905"

if HF_TOKEN:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN
    )
else:
    client = None

def format_beers_context():
    """Formate la liste des bières via l'ORM Django"""
    # On utilise select_related pour optimiser la requête (récupère la brasserie en même temps)
    beers = Beer.objects.select_related('brewery_id').all()
    
    if not beers:
        return None
        
    context_list = []
    for b in beers:
        # Dans ton model, la Foreign Key s'appelle 'brewery_id', donc Django utilise ce nom pour l'objet lié
        brasserie = b.brewery_id
        desc = b.description
        
        # On formate avec toutes les infos utiles au sommelier (Ville, Degré, Amertume)
        line = (
            f"- {b.name} (Brasserie {brasserie.name} à {brasserie.city}) | "
            f"Alcool: {b.degree}% | "
            f"Amertume: {b.bitterness} | "
            f"Description: {desc}"
        )
        context_list.append(line)
        
    return "\n".join(context_list)

@require_POST
def chat_api(request):
    """L'équivalent de votre endpoint @router.post('/chat')"""
    if not client:
        return JsonResponse({"response": "Erreur: Token HF_TOKEN_READ manquant côté serveur."}, status=500)

    try:
        # Lire le JSON envoyé par le JS
        data = json.loads(request.body)
        user_message = data.get('message', '')
    except json.JSONDecodeError:
        return JsonResponse({"response": "Erreur de format JSON."}, status=400)

    beers_context = format_beers_context() or "Aucune bière en stock."

    messages = [
        {
            "role": "system",
            "content": f"""Tu es Gaétan, un sommelier bière expert.
            Ton stock est LIMITÉ à cette liste :
            {beers_context}
            
            Consignes :
            - Ne recommande QUE des bières de cette liste.
            - Si on te demande une bière hors liste, dis poliment qu'elle n'est pas en stock.
            - Réponds en français."""
        },
        {
            "role": "user", 
            "content": user_message
        }
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=False
        )
        return JsonResponse({"response": response.choices[0].message.content})

    except Exception as e:
        print(f"❌ Erreur API : {str(e)}")
        return JsonResponse({"response": "Désolé, le sommelier est momentanément indisponible."}, status=500)

@ensure_csrf_cookie
def index(request):
    month = timezone.now().month
    year = timezone.now().year
    top10 = Beer.objects.annotate(avg_rating=Avg('drinks__note')).order_by('-avg_rating')[:10]
    top10Month = Beer.objects.annotate(avg_rating=Avg('drinks__note', filter=Q(drinks__date__year=year, drinks__date__month=month))).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]

    context = {"top":top10, "topMonth":top10Month}
    return render(request, "home.html", context)