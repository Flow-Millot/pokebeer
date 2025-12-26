import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Récupération de l'URL depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

# Si la variable est vide, on arrête tout de suite pour éviter de tourner en rond
if not DATABASE_URL:
    raise ValueError("❌ Erreur critique : La variable d'environnement DATABASE_URL n'est pas définie.")

# Correction automatique pour SQLAlchemy (il n'aime pas "postgres://", il veut "postgresql://")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuration du moteur de base de données
# On tente de se connecter en boucle jusqu'à réussite (utile au démarrage)
engine = None
while True:
    try:
        print("🔄 Tentative de connexion à la base de données...")
        engine = create_engine(DATABASE_URL)
        # Test réel de connexion
        with engine.connect() as connection:
            print("✅ Connexion à la base de données réussie !")
        break
    except Exception as e:
        print(f"❌ Échec de la connexion. Erreur : {e}")
        print("⏳ Nouvelle tentative dans 5 secondes...")
        time.sleep(5)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dépendance pour récupérer la session DB dans les routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()