from fastapi import APIRouter, Depends, status, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.database import SessionLocal
from app.routers.auth import get_current_user
from app.models import Products, Recipes, RecipeItems

router = APIRouter(
    prefix="/recipe-item",
    tags=["recipe-item"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class RecipeItemsRequest(BaseModel):
    recipe_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

@router.get("", status_code=status.HTTP_200_OK)
async def get_recipe_items(user: user_dependency, db: db_dependency, recipe_id: Optional[int|None]=Query(default=None, gt=0), product_id: Optional[int|None]=Query(default=None, gt=0)):
    recipe_item_model = db.query(RecipeItems)
    if recipe_id is not None:
        recipe_item_model = recipe_item_model.filter(RecipeItems.recipe_id == recipe_id)
    if product_id is not None:
        recipe_item_model = recipe_item_model.filter(RecipeItems.product_id == product_id)
    items = recipe_item_model.all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe item not found")
    return items

@router.get("/{recipe_item_id}", status_code=status.HTTP_200_OK)
async def get_recipe_item_by_id(user: user_dependency, db: db_dependency, recipe_item_id: int=Path(gt=0)):
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == recipe_item_id).first()
    if recipe_item_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe item not found")
    return recipe_item_model

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_recipe_item(user: user_dependency, db: db_dependency, request: RecipeItemsRequest):
    recipe_model = db.query(Recipes).filter(Recipes.id == request.recipe_id).first()
    product_model = db.query(Products).filter(Products.id == request.product_id).first()
    if not product_model and not recipe_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe and product not found")
    if not recipe_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if not product_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    recipe_item_model = RecipeItems(**request.model_dump())
    db.add(recipe_item_model)
    db.commit()
    db.refresh(recipe_item_model)
    return recipe_item_model

@router.put("/{recipe_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_recipe_item(user: user_dependency, db: db_dependency, recipe_item_id: int, request: RecipeItemsRequest):
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == recipe_item_id).first()
    if not recipe_item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe item not found")
    recipe_model = db.query(Recipes).filter(Recipes.id == request.recipe_id).first()
    product_model = db.query(Products).filter(Products.id == request.product_id).first()
    if not product_model and not recipe_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe and product not found")
    if not recipe_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if not product_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    recipe_item_model.recipe_id = request.recipe_id
    recipe_item_model.product_id = request.product_id
    recipe_item_model.quantity = request.quantity
    db.commit()

@router.delete("/{recipe_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_item(user: user_dependency, db: db_dependency, recipe_item_id: int):
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == recipe_item_id).first()
    if not recipe_item_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe item not found")
    db.delete(recipe_item_model)
    db.commit()