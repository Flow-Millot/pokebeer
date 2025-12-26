from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth, beers, pages, chatbot

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PokeBeer")

app.include_router(auth.router)
app.include_router(beers.router)
app.include_router(pages.router)
app.include_router(chatbot.router)