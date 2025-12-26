from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from . import models

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username, hashed_password):
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_beer(db: Session, name: str, brewery: str, user_id: int):
    db_beer = models.Beer(name=name, brewery=brewery, adder_id=user_id)
    db.add(db_beer)
    db.commit()
    db.refresh(db_beer)
    return db_beer

def rate_beer(db: Session, beer_id: int, user_id: int, score: int):
    # Check if rating exists
    existing = db.query(models.Rating).filter(
        models.Rating.beer_id == beer_id, 
        models.Rating.user_id == user_id
    ).first()
    
    if existing:
        existing.score = score
        existing.created_at = func.now() # Update time for "month" logic
    else:
        new_rating = models.Rating(beer_id=beer_id, user_id=user_id, score=score)
        db.add(new_rating)
    db.commit()

def get_top_beers(db: Session, limit: int = 10, days: int = None):
    """
    Returns beers ordered by average rating.
    If days is provided, filters ratings by the last X days (e.g., 30 for month).
    """
    query = db.query(
        models.Beer,
        func.avg(models.Rating.score).label("average_score"),
        func.count(models.Rating.id).label("rating_count")
    ).join(models.Rating)

    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(models.Rating.created_at >= cutoff)

    query = query.group_by(models.Beer.id).order_by(desc("average_score")).limit(limit)
    return query.all()

def get_all_beers(db: Session):
    return db.query(models.Beer).all()