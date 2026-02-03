from starlette import status

from test.utils import *
from app.routers.users import get_db, get_current_user
from app.main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] ==  'myusername'
    assert response.json()['email'] ==  'test@email.com'
    assert response.json()['first_name'] ==  'firstname'
    assert response.json()['last_name'] ==  'lastname'
    assert response.json()['role'] ==  'admin'