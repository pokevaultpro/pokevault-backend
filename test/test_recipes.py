from starlette import status

from test.utils import *
from app.routers.recipes import get_db, get_current_user
from app.main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_recipe(test_recipe):
    response = client.get(f"/recipe")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'name': 'Carbonara', 'id': 1, 'owner_id': 1, 'image': None},
                               {'name': 'Risotto ai Funghi', 'id': 2, 'owner_id': 2, 'image': None}]

def test_get_recipe_by_owner_id(test_recipe):
    response = client.get(f"/recipe?owner_id={test_recipe[0].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'name': 'Carbonara', 'id': 1, 'owner_id': 1, 'image': None}]

def test_get_recipe_by_owner_id_not_found(test_recipe):
    response = client.get("/recipe?owner_id=9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

def test_get_recipe_by_id(test_recipe):
    response = client.get(f"/recipe/{test_recipe[0].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'name': 'Carbonara', 'id': test_recipe[0].id, 'owner_id': 1, 'image': None}

def test_get_recipe_by_id_not_found(test_recipe):
    response = client.get("/recipe/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}

def test_create_recipe(test_recipe):
    request_data = {'name': 'New Recipe', 'owner_id': 1}
    response = client.post("/recipe", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    new_recipe = response.json()
    new_recipe_id = new_recipe['id']
    db = TestingSessionLocal()
    recipe_model = db.query(Recipes).filter(Recipes.id == new_recipe_id).first()
    assert recipe_model is not None
    assert recipe_model.name == request_data['name']
    assert recipe_model.owner_id == request_data['owner_id']

def test_create_recipe_wrong_owner_id(test_recipe):
    request_data = {'name': 'New Recipe', 'owner_id': 9999}
    response = client.post("/recipe", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Wrong user id'}

def test_update_recipe(test_recipe):
    request_data = {'name': 'New Recipe', 'owner_id': 2}
    response = client.put(f"/recipe/{test_recipe[0].id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    recipe_model = db.query(Recipes).filter(Recipes.id == test_recipe[0].id).first()
    assert recipe_model is not None
    assert recipe_model.name == request_data['name']
    assert recipe_model.owner_id == request_data['owner_id']

def test_update_recipe_wrong_user_id(test_recipe):
    request_data = {'name': 'New Recipe', 'owner_id': 9999}
    response = client.put(f"/recipe/{test_recipe[0].id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Wrong user id'}

    db = TestingSessionLocal()
    recipe_model = db.query(Recipes).filter(Recipes.id == test_recipe[0].id).first()
    assert recipe_model is not None
    assert recipe_model.name != request_data['name']
    assert recipe_model.owner_id != request_data['owner_id']

def test_update_recipe_not_found(test_recipe):
    request_data = {'name': 'New Recipe', 'owner_id': 2}
    response = client.put("/recipe/9999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}

def test_delete_recipe(test_recipe):
    response = client.delete(f"/recipe/{test_recipe[0].id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    recipe_model = db.query(Recipes).filter(Recipes.id == test_recipe[0].id).first()
    assert recipe_model is None

def test_delete_recipe_not_found(test_recipe):
    response = client.delete("/recipe/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}