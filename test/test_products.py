from starlette import status

from test.utils import *
from app.routers.products import get_db, get_current_user
from app.main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_products(test_product):
    response = client.get('/product')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 3.2, 'name': 'Onion',
                               'supermarket_id': 1, 'original_price': 0.62, 'id': 1, 'image': None,
                                'unit': 'pz', 'category': 'Frutta', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None},
                               {'aisle_order': 2.5, 'name': 'Garlic',
                               'supermarket_id': 2, 'original_price': 0.88, 'id': 2, 'image': None,
                                'unit': '100g', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None
                                },
                               {'aisle_order': 3, 'name': 'Swile',
                                'supermarket_id': 1, 'original_price': 1.24, 'id': 3, 'image': None,
                                'unit': 'pz', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': 1.10, 'location': None
                                }
                               ]

def test_get_product_by_id(test_product):
    response = client.get(f'/product/{test_product[0].id}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'aisle_order': 3.2, 'name': 'Onion',
                               'supermarket_id': 1, 'original_price': 0.62, 'id': 1, 'image': None,
                                'unit': 'pz', 'category': 'Frutta', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None}

def test_get_product_by_id_not_found(test_product):
    response = client.get('/product/9999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

def test_get_products_by_supermarket_query(test_product):
    supermarket_id = test_product[0].supermarket_id
    response = client.get(f"/product?supermarket_id={supermarket_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert data[0]["supermarket_id"] == supermarket_id
    assert data[0]["name"] == "Onion"

def test_get_products_by_supermarket_path(test_product):
    supermarket_id = test_product[0].supermarket_id
    response = client.get(f"/product/supermarket/{supermarket_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 3, 'name': 'Swile',
                                'supermarket_id': 1, 'original_price': 1.24, 'id': 3, 'image': None,
                                'unit': 'pz', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': 1.10, 'location': None
                                }, {'aisle_order': 3.2, 'name': 'Onion',
                               'supermarket_id': 1, 'original_price': 0.62, 'id': 1, 'image': None,
                                'unit': 'pz', 'category': 'Frutta', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None}]

def test_get_products_by_category(test_product):
    category = test_product[1].category
    response = client.get(f"/product?category={category}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 2.5, 'name': 'Garlic',
                               'supermarket_id': 2, 'original_price': 0.88, 'id': 2, 'image': None,
                                'unit': '100g', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None
                                },
                               {'aisle_order': 3, 'name': 'Swile',
                                'supermarket_id': 1, 'original_price': 1.24, 'id': 3, 'image': None,
                                'unit': 'pz', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': 1.10, 'location': None
                                }
                               ]

def test_get_products_by_search(test_product):
    name = test_product[1].name
    response = client.get(f"/product?search={name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 2.5, 'name': 'Garlic',
                               'supermarket_id': 2, 'original_price': 0.88, 'id': 2, 'image': None,
                                'unit': '100g', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None
                                }]

def test_get_products_by_search_partial_name(test_product):
    name = 'Garl'
    response = client.get(f"/product?search={name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 2.5, 'name': 'Garlic',
                               'supermarket_id': 2, 'original_price': 0.88, 'id': 2, 'image': None,
                                'unit': '100g', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None
                                }]

def test_get_products_discounted_only(test_product):
    discounted_only = True
    response = client.get(f"/product?discounted_only={discounted_only}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 3, 'name': 'Swile',
                                'supermarket_id': 1, 'original_price': 1.24, 'id': 3, 'image': None,
                                'unit': 'pz', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': 1.10, 'location': None
                                }]

def test_get_products_by_search_and_category(test_product):
    category = test_product[1].category
    name = test_product[1].name
    response = client.get(f"/product?category={category}&search={name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'aisle_order': 2.5, 'name': 'Garlic',
                               'supermarket_id': 2, 'original_price': 0.88, 'id': 2, 'image': None,
                                'unit': '100g', 'category': 'Verdura', 'calories': None, 'fat': None, 'carbs': None,
                                'protein': None, 'discounted_price': None, 'location': None
                                }]


def test_get_products_by_supermarket_query_not_found(test_product):
    response = client.get("/product?supermarket_id=9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Supermarket not found"}

def test_get_products_by_supermarket_path_not_found(test_product):
    response = client.get("/product/supermarket/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Supermarket not found"}

def test_create_product(test_product):
    request_data = {'name': 'New Product', 'category': 'Meat', 'unit': 'pz',
                    'location': 'Corridoio 3','supermarket_id': 2, 'original_price': 2.30,
                    'discounted_price': 2.00, 'aisle_order': 3.00}
    response = client.post('/product', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    created_product = response.json()
    created_product_id = created_product['id']
    db = TestingSessionLocal()
    product_model = db.query(Products).filter(Products.id == created_product_id).first()
    assert product_model is not None
    assert product_model.name == request_data["name"]
    assert product_model.discounted_price == request_data["discounted_price"]
    assert product_model.aisle_order == request_data["aisle_order"]
    assert product_model.supermarket_id == request_data["supermarket_id"]
    assert product_model.original_price == request_data["original_price"]
    assert product_model.unit == request_data["unit"]
    assert product_model.category == request_data["category"]
    assert product_model.location == request_data["location"]


def test_create_product_supermarket_not_found(test_product):
    request_data = {'name': 'New Product', 'category': 'Meat', 'unit': 'pz',
                    'location': 'Corridoio 3', 'supermarket_id': 9999, 'original_price': 2.30,
                    'discounted_price': 2.00, 'aisle_order': 3.00}
    response = client.post('/product', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Supermarket id not found"}

    db = TestingSessionLocal()
    product_model = db.query(Products).filter(Products.name == "New Product").first()
    assert product_model is None


def test_update_product(test_product):
    request_data = {'name': 'Updated Product', 'unit': '200g', 'supermarket_id': 1, 'original_price': 5.20,
                    'aisle_order': 1.20, 'discounted_price': 1.00}
    response = client.put(f"/product/{test_product[0].id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    product_model = db.query(Products).filter(Products.id == test_product[0].id).first()
    assert product_model is not None
    assert product_model.name == request_data["name"]
    assert product_model.original_price == request_data["original_price"]
    assert product_model.aisle_order == request_data["aisle_order"]
    assert product_model.supermarket_id == request_data["supermarket_id"]
    assert product_model.unit == request_data["unit"]
    assert product_model.discounted_price == request_data["discounted_price"]



def test_update_product_not_found(test_product):
    request_data = {'name': 'Updated Product', 'supermarket_id': 1, 'price': 5.20, 'aisle_order': 1.20}
    response = client.put('/product/9999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}

def test_delete_product(test_product):
    response = client.delete(f"/product/{test_product[0].id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    product_model = db.query(Products).filter(Products.id == test_product[0].id).first()
    assert product_model is None

def test_delete_product_not_found(test_product):
    response = client.delete("/product/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Product not found"}
