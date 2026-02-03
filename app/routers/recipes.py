from fastapi import APIRouter, Depends, Path, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from starlette import status

from app.database import SessionLocal
from app.routers.auth import get_current_user
from app.models import Recipes, Users

router = APIRouter(
    prefix="/recipe",
    tags=["recipe"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class RecipeRequest(BaseModel):
    name: str = Field(min_length=2)
    owner_id: int = Field(gt=0)
    image: str | None = None

@router.get("", status_code=status.HTTP_200_OK)
async def get_recipes(user: user_dependency, db: db_dependency, owner_id: Optional[int]=Query(default=None, gt=0)):
    if owner_id:
        user_model = db.query(Users).filter(Users.id == owner_id).first()
        if not user_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return db.query(Recipes).filter(Recipes.owner_id == owner_id).all()
    return db.query(Recipes).all()

@router.get("/{recipe_id}", status_code=status.HTTP_200_OK)
async def get_recipe_by_id(user: user_dependency, db: db_dependency, recipe_id: int=Path(gt=0)):
    recipe_model = db.query(Recipes).filter(Recipes.id == recipe_id).first()
    if recipe_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe_model

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_recipe(user: user_dependency, db: db_dependency, request: RecipeRequest):
    owner_id = request.owner_id
    #user_model = db.query(Users).filter(Users.id == owner_id).filter(Users.id == user.get('id')).first()
    user_model = db.query(Users).filter(Users.id == owner_id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong user id")
    recipe_model = Recipes(**request.model_dump())
    db.add(recipe_model)
    db.commit()
    db.refresh(recipe_model)
    return recipe_model

@router.put("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_recipe(user: user_dependency, db: db_dependency, recipe_id: int, request: RecipeRequest):
    user_id = request.owner_id
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong user id")
    recipe_model = db.query(Recipes).filter(Recipes.id == recipe_id).first()
    if recipe_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    recipe_model.name = request.name
    recipe_model.owner_id = request.owner_id
    db.commit()

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(user: user_dependency, db: db_dependency, recipe_id: int):
    recipe_model = db.query(Recipes).filter(Recipes.id == recipe_id).first()
    if recipe_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    db.delete(recipe_model)
    db.commit()