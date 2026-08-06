from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")
# print(f"DUMMY_HASH: {DUMMY_HASH}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    print(f"authenticate_user: user={user}")
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user







#TODO ENDPOINTS


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")



#TODO /token endpoint flow diagram

#                 POST /token
#                       │
#                       ▼
# login_for_access_token()
#                       │
#                       ▼
# FastAPI executes Depends()
#                       │
#                       ▼
# OAuth2PasswordRequestForm
# (username + password)
#                       │
#                       ▼
# form_data.username
# form_data.password
#                       │
#                       ▼
# authenticate_user()
#                       │
#           ┌───────────┴───────────┐
#           │                       │
#           ▼                       ▼
#      get_user()              User not found
#           │                       │
#           ▼                       ▼
#    UserInDB object         verify dummy password
#           │                       │
#           ▼                       ▼
# verify_password()           return False
#           │
#    ┌──────┴──────┐
#    │             │
#    ▼             ▼
# Password OK   Password Wrong
#    │             │
#    ▼             ▼
# create_access_token()   HTTP 401
#    │
#    ▼
# JWT generated
# (sub=username, exp=time)
#    │
#    ▼
# Return Token
# {
#   access_token,
#   token_type="bearer"
# }







@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


#TODO /users/me/ endpoint flow diagram

#             GET /users/me/
#                   │
#                   ▼
# read_users_me()
#                   │
#                   ▼
# Depends(get_current_active_user)
#                   │
#                   ▼
# get_current_active_user()
#                   │
#                   ▼
# Depends(get_current_user)
#                   │
#                   ▼
# OAuth2PasswordBearer
#                   │
#                   ▼
# Reads Authorization Header

# Authorization: Bearer <token>
#                   │
#                   ▼
# Extract token
#                   │
#                   ▼
# get_current_user(token)
#                   │
#                   ▼
# jwt.decode(token)
#                   │
#       ┌───────────┴───────────┐
#       │                       │
#       ▼                       ▼
#  Token Invalid          Token Valid
#       │                       │
#       ▼                       ▼
#  HTTP 401              username = payload["sub"]
#                               │
#                               ▼
#                      get_user(fake_users_db)
#                               │
#                     ┌─────────┴─────────┐
#                     │                   │
#                     ▼                   ▼
#                User Found         User Missing
#                     │                   │
#                     ▼                   ▼
#              return User         HTTP 401
#                     │
#                     ▼
# get_current_active_user()
#                     │
#          ┌──────────┴──────────┐
#          │                     │
#          ▼                     ▼
#  disabled=True          disabled=False
#          │                     │
#          ▼                     ▼
#      HTTP 400             return User
#                                   │
#                                   ▼
#                        read_users_me(current_user)
#                                   │
#                                   ▼
#                           Return current user




@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]




#TODO /users/me/items/ endpoint flow diagram



#          GET /users/me/items/
#                   │
#                   ▼
# read_own_items()
#                   │
#                   ▼
# Depends(get_current_active_user)
#                   │
#                   ▼
# get_current_active_user()
#                   │
#                   ▼
# Depends(get_current_user)
#                   │
#                   ▼
# OAuth2PasswordBearer
#                   │
#                   ▼
# Authorization Header
# (Bearer Token)
#                   │
#                   ▼
# Extract Token
#                   │
#                   ▼
# jwt.decode()
#                   │
#                   ▼
# Extract username
#                   │
#                   ▼
# get_user()
#                   │
#                   ▼
# User exists?
#           │
#      ┌────┴────┐
#      │         │
#      ▼         ▼
#    No         Yes
#      │         │
#      ▼         ▼
# HTTP 401   disabled?
#                │
#         ┌──────┴──────┐
#         │             │
#         ▼             ▼
#       Yes            No
#         │             │
#         ▼             ▼
#     HTTP 400     return User
#                         │
#                         ▼
# read_own_items(current_user)
#                         │
#                         ▼
# Return
# [
#   {
#     "item_id": "Foo",
#     "owner": current_user.username
#   }
# ]