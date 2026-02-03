from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status

from app.database import SessionLocal
from app.routers.auth import get_current_user
from app.models import Supermarkets, Products

router = APIRouter(
    prefix="/supermarket",
    tags=["supermarket"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class SupermarketRequest(BaseModel):
    name: str = Field(min_length=2, max_length=15)
    image: str | None = None
    location: str | None = None

class SupermarketUpdate(BaseModel):
    name: str = Field(default=None, min_length=2, max_length=15)
    image: str | None = None
    location: str | None = None

@router.get("", status_code=status.HTTP_200_OK)
async def get_supermarkets(user: user_dependency, db: db_dependency):
    return db.query(Supermarkets).all()

@router.get("/{supermarket_id}/products", status_code=status.HTTP_200_OK)
async def get_supermarket_products(user: user_dependency, db: db_dependency, supermarket_id: int = Path(gt=0)):
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
    if supermarket_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
    return (db.query(Products).filter(Products.supermarket_id == supermarket_id)
            .order_by(Products.aisle_order).all())

@router.get("/{supermarket_id}", status_code=status.HTTP_200_OK)
async def get_supermarket_by_id(user: user_dependency, db: db_dependency, supermarket_id: int=Path(gt=0)):
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
    if supermarket_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
    return supermarket_model

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_supermarket(user: user_dependency, db: db_dependency, request: SupermarketRequest):
    normalized_name = request.name.strip().lower()
    existing = db.query(Supermarkets).filter(func.lower(Supermarkets.name) == normalized_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Supermarket with this name already exists")
    data = request.model_dump()
    data['name'] = normalized_name.capitalize()
    supermarket_model = Supermarkets(**data)
    db.add(supermarket_model)
    db.commit()
    db.refresh(supermarket_model)
    return supermarket_model

@router.put("/{supermarket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_supermarket(user: user_dependency, db: db_dependency, supermarket_id: int, request: SupermarketUpdate):
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
    if supermarket_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supermarket_model, key, value)
    db.commit()

@router.delete("/{supermarket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supermarket(user: user_dependency, db: db_dependency, supermarket_id: int):
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
    if supermarket_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
    db.delete(supermarket_model)
    db.commit()