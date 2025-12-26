from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from .. import database, crud, dependencies

router = APIRouter()

@router.post("/add_beer")
def add_beer(
    name: str = Form(...),
    brewery: str = Form(...),
    user=Depends(dependencies.require_user),
    db: Session = Depends(database.get_db)
):
    crud.create_beer(db, name, brewery, user.id)
    return RedirectResponse(url="/", status_code=303)

@router.post("/rate_beer")
def rate_beer(
    beer_id: int = Form(...),
    score: int = Form(...),
    user=Depends(dependencies.require_user),
    db: Session = Depends(database.get_db)
):
    if 1 <= score <= 5:
        crud.rate_beer(db, beer_id, user.id, score)
    return RedirectResponse(url="/", status_code=303)