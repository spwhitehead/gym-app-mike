from uuid import uuid4 as new_uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine
from models.user import User
from models.requests import CreateUserRequest, UpdateUserRequest
from models.responses import ResponseUser, ResponseUserList, UserData

router = APIRouter()

# User End Points
@router.get("/users", response_model=ResponseUserList, status_code=status.HTTP_200_OK)
async def get_users() -> ResponseUserList:
    with Session(bind=engine) as session:
        users = session.exec(select(User)).all()
        data = [UserData(**user.model_dump()) for user in users]
        return ResponseUserList(data=data, detail=f"{len(data)} users fetched successfully." if len(data) != 1 else f"{len(data)} user fetched successfully.")

@router.get("/users/{user_uuid}", response_model=ResponseUser, status_code=status.HTTP_200_OK)
async def get_user(user_uuid: UUID) -> ResponseUser:
    with Session(bind=engine) as session:
        user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    data = UserData(**user.model_dump())
    return ResponseUser(data=data, detail="User fetched successfully.")

@router.post("/users/", response_model=ResponseUser, status_code=status.HTTP_201_CREATED)
async def add_user(create_user_request: CreateUserRequest) -> ResponseUser:
    with Session(bind=engine) as session:
        uuid = new_uuid()
        session.exec(insert(User).values(uuid=uuid, **create_user_request.model_dump()))
        session.commit()
        user = session.exec(select(User).where(User.uuid == uuid)).first()
        data = UserData(**user.model_dump())
        return ResponseUser(data=data, detail="New User has been added.")

@router.put("/users/{user_uuid}", response_model=ResponseUser, status_code=status.HTTP_200_OK)
async def update_user(user_uuid: UUID, update_user_request: UpdateUserRequest) -> ResponseUser:
    with Session(bind=engine) as session:
        user = session.exec(select(User).where(User.uuid == user_uuid)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
        session.exec(update(User).where(User.uuid == user_uuid).values(
            first_name = update_user_request.first_name if update_user_request.first_name is not None else User.first_name,
            last_name = update_user_request.last_name if update_user_request.last_name is not None else User.last_name,
            birthday = update_user_request.birthday if update_user_request.birthday is not None else User.birthday,
            body_weight = update_user_request.body_weight if update_user_request.body_weight is not None else User.body_weight,
            height = update_user_request.height if update_user_request.height is not None else User.height,
            gender = update_user_request.gender if update_user_request.gender is not None else User.gender
        ))
        session.commit()
        session.refresh(user)
        data = UserData(**user.model_dump())
        return ResponseUser(data=data, detail="User updated.")
   
@router.delete("/users/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_user(user_uuid: UUID):
    with Session(bind=engine) as session:
        user = session.exec(select(User).where(User.uuid == user_uuid)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
        session.exec(delete(User).where(User.uuid == user_uuid))
        session.commit()