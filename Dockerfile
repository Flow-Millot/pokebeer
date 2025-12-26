FROM python:3.9

# 1. Créer un utilisateur non-root (Recommandé par HF)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Copier les requirements et installer
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Copier tout le code source (le dossier 'app' complet)
COPY --chown=user ./app /app/app

# 5. La commande de lancement
# Attention : on lance uvicorn sur le module app.main
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]