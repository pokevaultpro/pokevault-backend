from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from starlette import status

from app.database import SessionLocal
from app.routers.auth import get_current_user
from app.models import Products, Favorites

router = APIRouter(
    prefix="/favorite",
    tags=['favorite']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class FavoriteRequest(BaseModel):
    product_id: int = Field(gt=0)

@router.get("", status_code=status.HTTP_200_OK)
async def get_favorites(user: user_dependency, db: db_dependency):
    owner_id = user.get('id')
    favorite_model = db.query(Favorites.product_id).filter(Favorites.owner_id == owner_id).all()
    return [f[0] for f in favorite_model]

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(request: FavoriteRequest, user: user_dependency, db: db_dependency):
    product_id = request.product_id
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if not product_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    favorite_model = db.query(Favorites).filter(Favorites.owner_id == user.get('id')).filter(Favorites.product_id == product_id).first()
    if favorite_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already in favorites")
    favorite = Favorites(product_id=product_id, owner_id=user.get('id'))
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return {"status": "added", "product_id": product_id}

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(product_id: int, db: db_dependency, user: user_dependency):
    product_model = db.query(Products).filter(Products.id == product_id).first()
    if not product_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    favorite_model = db.query(Favorites).filter(Favorites.owner_id == user.get('id')).filter(Favorites.product_id == product_id).first()
    if not favorite_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
    db.delete(favorite_model)
    db.commit()
