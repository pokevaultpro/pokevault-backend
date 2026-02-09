from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from starlette import status
from datetime import datetime

from app.database import SessionLocal
from app.routers.auth import get_current_user
from app.models import Users, ShoppingHistory, ShoppingHistoryItem, Cart, Products

router = APIRouter(
    prefix="/shopping-history",
    tags=["shopping-history"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("", status_code=status.HTTP_200_OK)
async def get_shopping_history(user: user_dependency, db: db_dependency):
    owner_id = user.get("id")
    user_model = db.query(Users).filter(Users.id == owner_id).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    shopping_history_model = db.query(ShoppingHistory).filter(ShoppingHistory.user_id == owner_id).all()
    return shopping_history_model

@router.get("/{shopping_history_id}", status_code=status.HTTP_200_OK)
async def get_shopping_history_by_id(user: user_dependency, db: db_dependency, shopping_history_id: int=Path(gt=0)):
    shopping_history_model = (db.query(ShoppingHistory).filter(ShoppingHistory.id == shopping_history_id)
                              .filter(ShoppingHistory.user_id == user.get("id")).first())
    if shopping_history_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping History not found")
    return shopping_history_model

@router.get("/{shopping_history_id}/items", status_code=status.HTTP_200_OK)
async def get_shopping_history_items(user: user_dependency, db: db_dependency, shopping_history_id: int=Path(gt=0)):
    shopping_history_model = (db.query(ShoppingHistory).filter(ShoppingHistory.id == shopping_history_id)
                              .filter(ShoppingHistory.user_id == user.get("id")).first())
    if shopping_history_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping History not found")

    shopping_history_item_model = (db.query(ShoppingHistoryItem).filter
                                   (ShoppingHistoryItem.history_id == shopping_history_id)
                                   .all())
    return shopping_history_item_model

@router.post("/{shopping_history_id}/restore-cart", status_code=status.HTTP_201_CREATED)
async def shopping_history_restore_cart(user: user_dependency, db: db_dependency, shopping_history_id: int=Path(gt=0)):
    owner_id = user.get("id")
    shopping_history_model = (db.query(ShoppingHistory).filter(ShoppingHistory.id == shopping_history_id)
                              .filter(ShoppingHistory.user_id == owner_id).first())
    if shopping_history_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping History not found")

    shopping_history_item_model = (db.query(ShoppingHistoryItem).filter
                                   (ShoppingHistoryItem.history_id == shopping_history_id)
                                   .all())
    missing_products = []
    updated_products = []
    restored_products = []
    for item in shopping_history_item_model:
        product_model = db.query(Products).filter(Products.id == item.product_id).first()
        if product_model is None:
            missing_products.append({
                "id": item.product_id,
                "name": item.name,
                "category": item.category,
                "original_price": item.price_paid,
                "unit": item.unit,
                "supermarket_id": item.supermarket_id,
                "aisle_order": item.aisle_order,
                "image": item.image,
                "calories": item.calories,
                "fat": item.fat,
                "carbs": item.carbs,
                "protein": item.protein
            })
            continue
        changed = ((product_model.name != item.name) or
                   (product_model.category != item.category) or
                   (product_model.image != item.image) or
                   (product_model.unit != item.unit) or
                   (product_model.supermarket_id != item.supermarket_id) or
                   (product_model.original_price != item.price_paid and not item.was_discounted))
        if changed:
            updated_products.append({
                "id": item.product_id,
                "old": {
                    "name": item.name,
                    "category": item.category,
                    "unit": item.unit,
                    "supermarket_id": item.supermarket_id,
                    "image": item.image,
                    "original_price": item.price_paid,
                },
                "new": {
                    "name": product_model.name,
                    "category": product_model.category,
                    "unit": product_model.unit,
                    "supermarket_id": product_model.supermarket_id,
                    "image": product_model.image,
                    "original_price": product_model.original_price
                },
                "changed_fields": {
                    "name": product_model.name != item.name,
                    "category": product_model.category != item.category,
                    "unit": product_model.unit != item.unit,
                    "supermarket_id": product_model.supermarket_id != item.supermarket_id,
                    "image": product_model.image != item.image,
                    "original_price": (item.price_paid != product_model.original_price and not item.was_discounted)
                }
            })

        cart_model = Cart(
            product_id = item.product_id,
            quantity = item.quantity,
            owner_id = owner_id,
            checked = False
        )
        db.add(cart_model)
        restored_products.append(product_model.id)
    db.commit()
    return {"restored": restored_products, "updated": updated_products, "missing": missing_products}

@router.delete("/{shopping_history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_history(user: user_dependency, db: db_dependency, shopping_history_id: int):
    shopping_history_model = (db.query(ShoppingHistory).filter(ShoppingHistory.id == shopping_history_id)
                              .filter(ShoppingHistory.user_id == user.get("id")).first())
    if shopping_history_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping History not found")
    db.delete(shopping_history_model)
    db.commit()