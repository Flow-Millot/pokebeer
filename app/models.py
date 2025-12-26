from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    beers_added = relationship("Beer", back_populates="adder")
    ratings = relationship("Rating", back_populates="user")

class Beer(Base):
    __tablename__ = "beers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brewery = Column(String)
    adder_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    adder = relationship("User", back_populates="beers_added")
    ratings = relationship("Rating", back_populates="beer")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer) # 1 to 5
    user_id = Column(Integer, ForeignKey("users.id"))
    beer_id = Column(Integer, ForeignKey("beers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="ratings")
    beer = relationship("Beer", back_populates="ratings")