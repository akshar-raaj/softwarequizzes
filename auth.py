from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from passlib.context import CryptContext

from orm.models import User
from services import read_user, create_instance
from constants import ALGORITHM, SECRET_KEY, PLACEHOLDER_USER_EMAIL


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth_schema = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def decode_token(token) -> User:
    if token == 'abc':
        # Placeholder user
        user = read_user(PLACEHOLDER_USER_EMAIL)
        return user, ""
    try:
        data = jwt.decode(token, SECRET_KEY, ALGORITHM)
    except JWTError:
        return None, "Invalid token"
    email = data["sub"]
    user = read_user(email)
    if user is None:
        return None, "User not found"
    return user, ""


def encode_token(data):
    token = jwt.encode(data, SECRET_KEY, ALGORITHM)
    return token


def get_current_user(token: Annotated[str, Depends(oauth_schema)]):
    user, details = decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail=details)
    return user


def authenticate(form_data: OAuth2PasswordRequestForm) -> dict:
    email = form_data.username
    password = form_data.password
    user = read_user(email)
    if user is None:
        return None, "User not found"
    if verify_password(password, user.password) is False:
        return None, "Incorrect password"
    data = {"sub": user.email}
    return encode_token(data), ""


def register_user(email: str, password: str):
    user = read_user(email)
    if user is not None:
        return None, "Email already taken"
    hashed_password = get_password_hash(password)
    data = {"email": email, "password": hashed_password}
    created_id = create_instance(User, data)
    user = read_user(email)
    data = {"sub": user.email}
    return encode_token(data), ""
    # return created_id, ""
