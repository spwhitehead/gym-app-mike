import datetime as dt
from typing import Annotated
from fastapi import Depends, APIRouter, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from db import get_db
from models.relationship_merge import User
from utilities.authorization import ACCESS_TOKEN_EXPIRE_MINUTES,Token, create_access_token, authenticate_user, get_current_user, check_roles

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, session)
    access_token_expires = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.uuid), "iat": dt.datetime.now(dt.UTC), "scopes": form_data.scopes}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# EXAMPLE

# @router.get("/users/me", response_model=User)
# @check_roles(["User", "Admin"])
# async def read_users_me(current_user: Annotated[User, Security(get_current_user, scopes=['User'])]):
#     return current_user
