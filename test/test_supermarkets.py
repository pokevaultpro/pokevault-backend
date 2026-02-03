from starlette import status

from test.utils import *
from app.routers.supermarkets import get_db, get_current_user
from app.main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_supermarket(test_supermarket):
    response = client.get(f"/supermarket")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'name': 'Conad', 'id': 1, 'image': None, 'location': 'Via delle Arti 22, Matera'},
                               {'name': 'Lidl', 'id': 2, 'image': None, 'location': 'Via delle Arti 1, Matera'}]

def test_get_supermarket_by_id(test_supermarket):
    response = client.get(f"/supermarket/{test_supermarket[0].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'name': 'Conad', 'id': test_supermarket[0].id,
                               'image': None, 'location': 'Via delle Arti 22, Matera'}

def test_get_supermarket_by_id_not_found(test_supermarket):
    response = client.get("/supermarket/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Supermarket not found'}

def test_get_supermarket_products(test_product):
    response = client.get(f"/supermarket/{test_product[0].supermarket_id}/products")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 3, 'name': 'Swile',
                                'supermarket_id': 1, 'original_price': 1.24, 'id': 3, 'image': None,
                                'unit': 'pz', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': 1.10, 'location': None
                                }, {'aisle_order': 3.2, 'name': 'Onion',
                               'supermarket_id': 1, 'original_price': 0.62, 'id': 1, 'image': None,
                                'unit': 'pz', 'category': 'Frutta', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None}]

def test_get_supermarket_products_not_found(test_supermarket):
    response = client.get("/supermarket/9999/products")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Supermarket not found'}

def test_create_supermarket(test_supermarket):
    request_data = {'name': 'New Supermarket', 'location': 'Via delle Arti 12, Matera'}
    response = client.post("/supermarket", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    new_supermarket = response.json()
    new_supermarket_id = new_supermarket['id']
    db = TestingSessionLocal()
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == new_supermarket_id).first()
    assert supermarket_model is not None
    assert supermarket_model.name == request_data['name'].strip().lower()
    assert supermarket_model.location == request_data['location']

def test_create_duplicate_supermarket(test_supermarket):
    request_data = {'name': 'Conad', 'location': 'Via delle Arti 12, Matera'}
    response = client.post("/supermarket", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Supermarket with this name already exists'}

def test_update_supermarket(test_supermarket):
    request_data = {'name': 'New Supermarket'}
    response = client.put(f"/supermarket/{test_supermarket[0].id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == test_supermarket[0].id).first()
    assert supermarket_model is not None
    assert supermarket_model.name == request_data['name']

def test_update_supermarket_not_found(test_supermarket):
    request_data = {'name': 'New Supermarket'}
    response = client.put("/supermarket/9999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Supermarket not found'}

def test_delete_supermarket(test_supermarket):
    response = client.delete(f"/supermarket/{test_supermarket[0].id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    supermarket_model = db.query(Supermarkets).filter(Supermarkets.id == test_supermarket[0].id).first()
    assert supermarket_model is None

def test_delete_supermarket_not_found(test_supermarket):
    response = client.delete("/supermarket/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Supermarket not found'}