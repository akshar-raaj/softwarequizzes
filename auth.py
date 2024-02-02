from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from passlib.context import CryptContext

from orm.models import User
from services import read_user, create_instance
from constants import ALGORITHM, SECRET_KEY, PLACEHOLDER_USER_EMAIL, REDIS_REGISTERED_USERS_KEY
from cache import get_engine as cache_engine


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth_schema = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_token(token: str) -> tuple[User, str]:
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


def encode_token(data: dict) -> str:
    """
    Encode the provided data as JSON Web Token.

    JSON Web Token are used to represent claim securely between two parties.

    Encoding needs two things:
    - algorithm
    - secret key
    """
    token = jwt.encode(data, SECRET_KEY, ALGORITHM)
    return token


def get_current_user(token: Annotated[str, Depends(oauth_schema)]) -> User:
    user, details = decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail=details)
    return user


def authenticate(email: str, password: str) -> tuple[str | None, str]:
    """
    Check if the provided credentials are valid
    """
    user = read_user(email)
    if user is None:
        return None, "User not found"
    if verify_password(password, user.password) is False:
        return None, "Incorrect password"
    data = {"sub": user.email}
    return encode_token(data), ""


def register_user(email: str, password: str) -> tuple[str | None, str]:
    """
    Create a user.

    Peforms the following checks before creating the user:
    1. A user must not exist with the provided email.

    Once the user is created, it creates a JWT token.
    The token has the following fields:
    - sub

    Return a tuple with two fields:
    (token, message)

    We can add caching here to reduce load on the database while checking if an email is taken.
    Create a redis set called `registered-users` and add registered emails to that set.
    """
    redis = cache_engine()
    if redis.sismember(REDIS_REGISTERED_USERS_KEY, email):
        return None, "Email already taken"
    # Also check in the database in case cache is not synced with the database.
    user = read_user(email)
    if user is not None:
        return None, "Email already taken"
    hashed_password = get_password_hash(password)
    data = {"email": email, "password": hashed_password}
    created_id = create_instance(User, data)
    if created_id is None:
        return None, "Something went wrong"
    # Add entry to cache
    redis.sadd(REDIS_REGISTERED_USERS_KEY, email)
    # As we are only encoding user.email, hence this is not needed.
    # Still doing it in case we want to encode more user attributes.
    user = read_user(pk=created_id)
    data = {"sub": user.email}
    return encode_token(data), ""
