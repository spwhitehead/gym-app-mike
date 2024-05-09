from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from db import engine, get_db
from models.user import UserCreateReq, UserPatchReq
from models.relationship_merge import User
from models.responses import UserResponseData, UserResponse, UserListResponse
from models.relationship_merge import Role

router = APIRouter()

# User End Points
@router.get("/users", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def get_users(session: Session = Depends(get_db)) -> UserListResponse:
    users = session.exec(select(User)).all()
    data = [UserResponseData.model_validate(user) for user in users]
    return UserListResponse(data=data, detail=f"{len(data)} users fetched successfully." if len(data) != 1 else f"{len(data)} user fetched successfully.")

@router.get("/users/{user_uuid:uuid}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_uuid: UUID, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User fetched successfully.")

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_user(create_user_request: UserCreateReq, session: Session = Depends(get_db)) -> UserResponse:
    user = User.model_validate(create_user_request.model_dump())
    user_role = session.exec(select(Role).where(Role.name == "User")).first()
    user.roles.append(user_role)
    session.add(user)
    print(type(user.uuid))
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="New User has been added.")

@router.put("/users/{user_uuid:uuid}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(user_uuid: UUID, update_user_request: UserCreateReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    for attr, value in update_user_request.model_dump().items():
        setattr(user, attr, value) 
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/{user_uuid:uuid}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def patch_user(user_uuid: UUID, update_user_request: UserPatchReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    for attr, value in update_user_request.model_dump(exclude_unset=True).items():
        setattr(user, attr, value) 
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")
   
@router.delete("/users/{user_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_user(user_uuid: UUID, session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    session.delete(user)
    session.commit()