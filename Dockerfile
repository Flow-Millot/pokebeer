FROM python:3.12-slim

# Installation des outils système (netcat pour le wait-for-db)
RUN apt-get update && apt-get install -y build-essential libpq-dev netcat-traditional

# Création de l'utilisateur non-root (Requis par HF)
RUN useradd -m -u 1000 user

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code et changement de propriétaire
COPY --chown=user . .

# On donne les droits d'exécution au script
RUN chmod +x start.sh

# On bascule sur l'utilisateur
USER user

# Port Hugging Face par défaut
EXPOSE 7860

# Commande de lancement par défaut (HF utilisera ça)
CMD ["./start.sh"]
