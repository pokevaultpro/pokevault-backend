from starlette import status

from test.utils import *
from app.routers.favorites import get_db, get_current_user
from app.main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_favorites(test_favorite):
    response = client.get('/favorite')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [1]

def test_add_to_favorites(test_favorite):
    response = client.post('/favorite', json={'product_id': 3})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"status": "added", "product_id": 3}
    db = TestingSessionLocal()
    favorite_model = db.query(Favorites).filter(Favorites.owner_id == 1).filter(Favorites.product_id == 3).first()
    assert favorite_model is not None
    assert favorite_model.product_id == 3
    assert favorite_model.owner_id == 1
    assert favorite_model.id == 3

def test_add_to_favorites_product_not_found(test_favorite):
    response = client.post('/favorite', json={'product_id': 9999})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

def test_add_to_favorites_favorite_not_found(test_favorite):
    response = client.post('/favorite', json={'product_id': 1})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Product already in favorites"}

def test_remove_from_favorites(test_favorite):
    response = client.delete('/favorite/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    favorite_model = db.query(Favorites).filter(Favorites.product_id == 1).filter(Favorites.owner_id == 1).first()
    assert favorite_model is None

def test_remove_from_favorites_product_not_found(test_favorite):
    response = client.delete('/favorite/9999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

def test_remove_from_favorites_favorite_not_found(test_favorite):
    response = client.delete('/favorite/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Favorite not found"}