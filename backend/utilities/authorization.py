from uuid import UUID
import datetime as dt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel import SQLModel, Session, select
from sqlalchemy.orm import joinedload
from pydantic import ValidationError
from jose import JWTError, jwt
from bcrypt import checkpw
from decouple import config
from db import engine
from models.relationship_merge import User
from functools import wraps

SECRET_KEY = str(config("SECRET_KEY"))
ALGORITHM = str(config("ALGORITHM"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", scopes={})

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    user_uuid: UUID | None = None
    scopes: list[str] = []

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user(user_uuid: UUID, session: Session) -> User:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def authenticate_user(username: str, password: str, session: Session) -> User:
    user_uuid = session.exec(select(User.uuid).where(User.username == username)).first()
    user = get_user(user_uuid, session)
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user

def create_access_token(data: dict, expires_delta: dt.timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.now(dt.UTC) + expires_delta
    else:
        expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(security_scopses: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    if security_scopses.scopes:
        authenticate_value = f"Bearer scope={security_scopses.scopes}"
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: UUID = UUID(payload.get("sub"))
        if user_uuid is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(user_uuid=user_uuid, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise credentials_exception
    with Session(engine) as session:
        user = get_user(token_data.user_uuid, session) 
        if user is None:
            raise credentials_exception
        for scope in security_scopses.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return user

def check_roles(allowed_roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with Session(engine) as session:
                current_user: User = kwargs.get("current_user")
                current_user = session.exec(select(User).options(joinedload(User.roles)).where(User.uuid == current_user.uuid)).first()
                if current_user is None:
                        current_user = await get_current_user(*args, **kwargs)
                if current_user is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials were not provided")
                user_roles = set(role.name for role in current_user.roles)
                if not any(role in user_roles for role in allowed_roles):
                    raise HTTPException(status_code=403, detail="Not enough permissions")
                return await func(*args, **kwargs)
        return wrapper
    return decorator

