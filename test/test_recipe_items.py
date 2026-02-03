from starlette import status

from test.utils import *
from app.main import app
from app.routers.recipe_items import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_recipe_item(test_recipe_item):
    response = client.get("/recipe-item")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'recipe_id': 1, 'product_id': 1, 'quantity': 10, 'id': 1},
                               {'recipe_id': 1, 'product_id': 2, 'quantity': 5, 'id': 2},
                               {'recipe_id': 2, 'product_id': 1, 'quantity': 1, 'id': 3}]

def test_get_recipe_item_by_query_recipe(test_recipe_item):
    response = client.get(f"/recipe-item?recipe_id={test_recipe_item[0].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'recipe_id': 1, 'product_id': 1, 'quantity': 10, 'id': 1},
                               {'recipe_id': 1, 'product_id': 2, 'quantity': 5, 'id': 2}]

def test_get_recipe_item_by_query_product(test_recipe_item):
    response = client.get(f"/recipe-item?product_id={test_recipe_item[0].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'recipe_id': 1, 'product_id': 1, 'quantity': 10, 'id': 1},
                               {'recipe_id': 2, 'product_id': 1, 'quantity': 1, 'id': 3}]

def test_get_recipe_item_by_query_recipe_and_product(test_recipe_item):
    response = client.get(f"/recipe-item?recipe_id={test_recipe_item[0].id}"
                          f"&product_id={test_recipe_item[0].product_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'recipe_id': 1, 'product_id': 1, 'quantity': 10, 'id': 1}]

def test_get_recipe_item_by_query_recipe_not_found(test_recipe_item):
    response = client.get("/recipe-item?recipe_id=9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe item not found'}

def test_get_recipe_item_by_query_product_not_found(test_recipe_item):
    response = client.get("/recipe-item?product_id=9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe item not found'}

def test_get_recipe_item_by_query_recipe_and_product_not_found(test_recipe_item):
    response = client.get("/recipe-item?product_id=9999&recipe_id=9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe item not found'}

def test_get_recipe_item_by_id(test_recipe_item):
    response = client.get(f"/recipe-item/{test_recipe_item[0].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'recipe_id': 1, 'product_id': 1, 'quantity': 10, 'id': 1}

def test_get_recipe_item_by_id_not_found(test_recipe_item):
    response = client.get("/recipe-item/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe item not found'}

def test_create_recipe_item(test_recipe_item):
    request_data = {'recipe_id': 1, 'product_id': 1, 'quantity': 50}
    response = client.post("/recipe-item", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    new_recipe_item = response.json()
    new_recipe_item_id = new_recipe_item['id']
    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == new_recipe_item_id).first()
    assert recipe_item_model is not None

def test_create_recipe_item_recipe_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 9999, 'product_id': 1, 'quantity': 50}
    response = client.post("/recipe-item", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.recipe_id == request_data['recipe_id']).first()
    assert recipe_item_model is None

def test_create_recipe_item_product_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 1, 'product_id': 9999, 'quantity': 50}
    response = client.post("/recipe-item", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Product not found'}

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.product_id == request_data['product_id']).first()
    assert recipe_item_model is None

def test_create_recipe_item_recipe_id_and_product_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 9999, 'product_id': 9999, 'quantity': 50}
    response = client.post("/recipe-item", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe and product not found'}

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.recipe_id == request_data['recipe_id']).first()
    assert recipe_item_model is None

def test_update_recipe_item(test_recipe_item):
    request_data = {'recipe_id': 1, 'product_id': 1, 'quantity': 50}
    response = client.put(f"/recipe-item/{test_recipe_item[0].id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == test_recipe_item[0].id).first()
    assert recipe_item_model is not None
    assert recipe_item_model.recipe_id == request_data['recipe_id']
    assert recipe_item_model.product_id == request_data['product_id']
    assert recipe_item_model.quantity == request_data['quantity']

def test_update_recipe_item_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 1, 'product_id': 1, 'quantity': 50}
    response = client.put("/recipe-item/9999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe item not found'}

def test_update_recipe_item_recipe_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 9999, 'product_id': 1, 'quantity': 50}
    response = client.put(f"/recipe-item/{test_recipe_item[0].id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe not found'}

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == test_recipe_item[0].id).first()
    assert recipe_item_model is not None
    assert recipe_item_model.recipe_id != request_data['recipe_id']

def test_update_recipe_item_product_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 1, 'product_id': 9999, 'quantity': 50}
    response = client.put(f"/recipe-item/{test_recipe_item[0].id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Product not found'}

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == test_recipe_item[0].id).first()
    assert recipe_item_model is not None
    assert recipe_item_model.product_id != request_data['product_id']

def test_update_recipe_item_recipe_id_and_product_id_not_found(test_recipe_item):
    request_data = {'recipe_id': 9999, 'product_id': 9999, 'quantity': 50}
    response = client.put(f"/recipe-item/{test_recipe_item[0].id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe and product not found'}

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == test_recipe_item[0].id).first()
    assert recipe_item_model is not None
    assert recipe_item_model.recipe_id != request_data['recipe_id']

def test_delete_recipe_item(test_recipe_item):
    response = client.delete(f"/recipe-item/{test_recipe_item[0].id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    recipe_item_model = db.query(RecipeItems).filter(RecipeItems.id == test_recipe_item[0].id).first()
    assert recipe_item_model is None

def test_delete_recipe_item_not_found(test_recipe_item):
    response = client.delete("/recipe-item/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Recipe item not found'}