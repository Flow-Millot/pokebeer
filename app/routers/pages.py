from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import database, crud, dependencies

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home_page(request: Request, db: Session = Depends(database.get_db), user=Depends(dependencies.get_current_user)):
    top_all_time = crud.get_top_beers(db, limit=10)
    top_month = crud.get_top_beers(db, limit=10, days=30)
    all_beers = crud.get_all_beers(db) # To show list for rating
    
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "user": user,
        "top_all_time": top_all_time,
        "top_month": top_month,
        "all_beers": all_beers
    })

@router.get("/add-beer")
def add_beer_page(request: Request, user=Depends(dependencies.require_user)):
    return templates.TemplateResponse("add_beer.html", {"request": request, "user": user})

@router.get("/account")
def account_page(request: Request, user=Depends(dependencies.require_user)):
    return templates.TemplateResponse("account.html", {"request": request, "user": user})

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})