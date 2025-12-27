FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y build-essential libpq-dev
RUN apt-get update && apt-get install -y build-essential libpq-dev netcat-traditional

# Créer le dossier applicatif
WORKDIR /app

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

# Port exposé par Django
EXPOSE 8000
