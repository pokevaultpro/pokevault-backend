from starlette import status

from test.utils import *
from app.routers.shopping_history import get_db, get_current_user
from app.main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_shopping_history(test_shopping_history_item):
    response = client.get('/shopping-history')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'user_id': 1, 'total_items': 3, 'total_price': 5.50,
                                'created_at': "2024-01-01T10:00:00"},
                               {'id': 2, 'user_id': 1, 'total_items': 1, 'total_price': 2.00,
                                'created_at': "2024-01-02T10:00:00"}]

def test_get_shopping_history_by_id(test_shopping_history_item):
    response = client.get('/shopping-history/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id': 1, 'user_id': 1, 'total_items': 3,
                               'total_price': 5.50, 'created_at': "2024-01-01T10:00:00"}

def test_get_shopping_history_by_id_not_found(test_shopping_history_item):
    response = client.get('/shopping-history/9999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Shopping History not found'}

def test_get_shopping_history_items(test_shopping_history_item):
    response = client.get('/shopping-history/1/items')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'history_id': 1, 'product_id': 1, 'name': 'Onion', 'price_paid': 0.62,
                                'was_discounted': False, 'supermarket_id': 1, 'supermarket_name': 'Conad',
                                'aisle_order': 3.2, 'unit': 'pz', 'category': 'Frutta',
                                'image': "static/images/products/onion.png",'quantity': 3,
                                'calories': None, 'fat': None, 'carbs': None, 'protein': None},
                               {'id': 2, 'history_id': 1, 'product_id': 2, 'name': 'Garlic', 'price_paid': 0.88,
                                'was_discounted': False, 'supermarket_id': 2, 'supermarket_name': 'Lidl',
                                'aisle_order': 2.5, 'unit': '100g', 'category': 'Verdura',
                                'image': "static/images/products/garlic.png", 'quantity': 5,
                                'calories': None, 'fat': None, 'carbs': None, 'protein': None}]

def test_get_shopping_history_items_not_found(test_shopping_history_item):
    response = client.get('/shopping-history/9999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Shopping History not found'}

def test_shopping_history_restore_cart(test_shopping_history_item):
    response = client.post("/shopping-history/1/restore-cart")
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    cart_model = db.query(Cart).all()
    assert len(cart_model) == 2
    assert cart_model[0].product_id == 1
    assert cart_model[0].quantity == 3
    assert cart_model[0].owner_id == 1
    assert cart_model[0].checked == False

def test_delete_shopping_history(test_shopping_history_item):
    response = client.delete('/shopping-history/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    shopping_history_model = db.query(ShoppingHistory).filter(ShoppingHistory.id == 1).first()
    assert shopping_history_model is None

def test_delete_shopping_history_not_found(test_shopping_history_item):
    response = client.delete('/shopping-history/9999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Shopping History not found"}