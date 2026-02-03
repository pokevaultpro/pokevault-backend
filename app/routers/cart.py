from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from starlette import status

from app.database import SessionLocal
from app.routers.auth import get_current_user
from app.models import Cart, Products, Supermarkets

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class CartRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    checked: bool = False

class CartUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    checked: Optional[bool] = Field(default=None)

"""
@router.get("", status_code=status.HTTP_200_OK)
async def read_cart_of_everybody(user: user_dependency, db: db_dependency, supermarket_id: Optional[int] = Query(default=None, gt=0)):
    if supermarket_id is not None:
        supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
        if supermarket_model is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
        cart_model = db.query(Cart).join(Products).filter(Products.supermarket_id == supermarket_id).all()
        return cart_model
    return db.query(Cart).all()
"""

@router.get("", status_code=status.HTTP_200_OK)
async def read_cart(user: user_dependency, db: db_dependency, supermarket_id: Optional[int] = Query(default=None, gt=0)):
    if supermarket_id is not None:
        supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
        if supermarket_model is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
        cart_model = (db.query(Cart).join(Products).filter(Products.supermarket_id == supermarket_id)
                      .filter(Cart.owner_id == user.get('id')).all())
        return cart_model
    return db.query(Cart).filter(Cart.owner_id == user.get('id')).all()

@router.get("/{cart_id}", status_code=status.HTTP_200_OK)
async def read_cart_by_id(user: user_dependency, db: db_dependency, cart_id: int = Path(gt=0)):
        cart_model = db.query(Cart).filter(Cart.id == cart_id).filter(Cart.owner_id == user.get('id')).first()
        if cart_model is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return cart_model

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_cart(user: user_dependency, db: db_dependency, cart_request: CartRequest):
    product_model = db.query(Products).filter(Products.id == cart_request.product_id).first()
    if not product_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    existing = (db.query(Cart).filter(Cart.product_id == cart_request.product_id)
                .filter(Cart.owner_id == user.get('id')).first())
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already in cart")
    cart = Cart(**cart_request.model_dump(), owner_id=user.get('id'))
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

@router.put("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_cart(user: user_dependency, db: db_dependency, cart_update: CartUpdate, cart_id: int = Path(gt=0)):
    cart_model = db.query(Cart).filter(Cart.id == cart_id).filter(Cart.owner_id == user.get('id')).first()
    if cart_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if cart_update.checked is None and cart_update.quantity is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must update at least one field")
    if cart_update.quantity is not None:
        cart_model.quantity = cart_update.quantity
    if cart_update.checked is not None:
        cart_model.checked = cart_update.checked
    db.commit()

@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_id(user: user_dependency, db: db_dependency, cart_id: int = Path(gt=0)):
    cart_model = db.query(Cart).filter(Cart.id == cart_id).filter(Cart.owner_id == user.get('id')).first()
    if cart_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    db.delete(cart_model)
    db.commit()

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(user: user_dependency, db: db_dependency, supermarket_id: Optional[int] = Query(default=None, gt=0), checked: Optional[bool] = Query(default=None)):
    if supermarket_id is None and checked is None:
        deleted = db.query(Cart).filter(Cart.owner_id == user.get('id')).delete(synchronize_session=False)
        db.commit()
        if deleted == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return
    cart_model = db.query(Cart.id).join(Products).filter(Cart.owner_id == user.get('id'))
    if supermarket_id is not None:
        supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == supermarket_id).first()
        if supermarket_model is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supermarket not found")
        cart_model = cart_model.filter(Products.supermarket_id == supermarket_id)
    if checked is not None:
        cart_model = cart_model.filter(Cart.checked == checked)
    deleted = db.query(Cart).filter(Cart.id.in_(cart_model)).delete(synchronize_session=False)
    db.commit()
    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
