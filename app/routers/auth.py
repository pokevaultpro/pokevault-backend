from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt, JWTError

from app.database import SessionLocal
from app.models import Users

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = """MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCXYL+p/6vzqCYh
Q5mwaQIWXpwUQ0Niwz8wY2EbXr69FXjm4rIdSRsucoX+KxjwT5oKYX9+OT1dpD+u
pW5MS7bNYAys4/7QPqoXZBz+c+Pk7bRzCQbzV9fjzk4LEuVgKO7JRei8/aYrw99G
rNPcXG5+qIYKZEDe2WD4bg8w/qCCVFK7Qb0ZPU3KqgPCm5rS3nxMRQQstqzAif/K
B9STXLDsyKw6fnuc/aSD35E/MQxtHXeaQA2UcDIYUV/B31XUxwgeG3o5XB7EGYZg
r1Zz+EbQL3rGkF2WdtqnOtwL3605bF03oLP7nRoMr/sbkkpJ5ZawHNNMrKPnywCa
YJduvmQpAgMBAAECggEAJ5Z6qUeevWrlBd/66mKb1CPL55Sro8Fx3gKvW4wMj8B0
zNTORdBflmcG2bCFphr7KunSgL0RalLRAKhszvEiDlWnGvPJKMaqjtF0r6q5F55+
iXL76Vm4sO+8AzNe3yX1RJfOxNYExf9EfeQmx8M4dlE2NLOBL4Zj0LRfrq14Znyl
6yGAtM0CW38iwSDObhDz4O5DbuIiTm/TGWy8dJkBgzjnN1rjg/xT0Aq40sMRPEr5
4Fw76FOPSnd/foo8mtcmsga7ErXTZZr1ye18BgIdWaJQl2LVzxyfTjX4cBEMKxUI
DREhLDfyFNJI3/txtMkR6V/0YqzIDBax6uKv+hY+PQKBgQDFizwll8XvTORrzWmf
Mer+pw4OJNA4L4/PB3M6inYTwU5KBREoEsAL6uszU2xKEU85im2FTbcjKG5RDxLz
druiJ+KSrpNp4tWPXw9wKToKRTejGsdeuHlP6WaJ3ZJiv65SvL03MLJ6585bARLx
trZMOY/Ld98LgQICh/k890EYxwKBgQDELEBilJq8oTWR+qsrwbObfZm3kDvgHe7U
oHevoNR6qaRhCi8K0KtiQJTCVUh0wdHxtyBsVhX0ksoolUmYrRAzLKUt17HOmDCZ
3OBSgD6Jj2jKVkf4MPURDgU2zSV7KtBZ8RhMz49ecRkLigZkr2dLBid+mTQFN55w
D2CiSScLjwKBgASvIoP5r1XXSutLeZ+uvVXAfFLViKJsbkqIcLEIq3gYc1TJ/fgn
Sap+rYkQB1dSRcCliadJingo80S0yMxBGn3j2DmGLjSqjknSBTmxoJCxx3n0npme
YjIE5MuMF3aD+Qw5MXtnijPj3z7FLb/Rh00TaFd4xi8tpfCNbNmHO2HtAoGAMZQJ
daCe9rs7YbhbWEStEsgMeFLwfvSxrnUbqnxYFuQW0huTxgT0u3Ec53xMQo3VdGRW
wmqDQ/txMg6AuiBK7tQCrvJLUq4t4kTrQI5+v59J2ZEywSwGU5gagz4XkehBHeoL
vSXb0v98V+k7MmkODuzwQFORzRvAZAvO3VTllEsCgYAIsnycRB9tf5jiazyTDFWY
tsNvEFgVlqKeWi9AbXdsgSIwxlbQLH2jpOXEh7Tq/rUiIYY9c9P5bKD/J9/uUT/s
LxFdwzOcfsBB4Y6F7JowyqpWV7ddUyjkPtZPSplrVBcgdyqCrKCMfWUUHu5ITAuK
6uZZFgz0auW/bIIjrpbShg=="""

ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    to_encode = {"sub": username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: CreateUserRequest):
    create_user_model = Users(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=bcrypt_context.hash(user.password)
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model

@router.post("/token", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.username, user.id, user.role, timedelta(days=30))
    return {'access_token': token, 'token_type': 'bearer'}