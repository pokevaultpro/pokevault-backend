from jose import jwt
from datetime import timedelta
from fastapi import HTTPException, status

from app.routers.auth import get_db, get_current_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from test.utils import *

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user[0].username, "test", db)
    assert authenticated_user is not None

def test_authenticate_user_invalid_username(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user("WrongUsername", "test", db)
    assert authenticated_user is False

def test_authenticate_user_invalid_password(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user[0].username, "WrongPassword", db)
    assert authenticated_user is False

def test_create_access_token():
    username = "my_username"
    user_id = 2
    role = "admin"
    expires_delta = timedelta(minutes=5)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():

    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():

    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate user'

