from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Security
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from db import engine, get_db
from models.user import UserCreateReq, UserPatchReq, UserPutReq, UserUsernamePatchReq, UserPasswordPatchReq, UserRolePatchReq
from models.relationship_merge import User
from models.responses import UserResponseData, UserResponse, UserListResponse
from models.relationship_merge import Role
from utilities.authorization import check_roles, get_current_user
import logging

router = APIRouter()

def setup_logging():
    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the minimum level to capture all logs

    # Create file handler which logs even debug messages
    fh = logging.FileHandler('debug.log')
    fh.setLevel(logging.DEBUG)  # Ensure the handler captures all debug logs

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(fh)

setup_logging()

# Get Requests 
@router.get("/users/all", response_model=UserListResponse, status_code=status.HTTP_200_OK)
@check_roles(["Admin"])
async def get_users_and_admins(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> UserListResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    users = session.exec(select(User)).all()
    data = [UserResponseData.model_validate(user) for user in users]
    return UserListResponse(data=data, detail=f"{len(data)} users fetched successfully." if len(data) != 1 else f"{len(data)} user fetched successfully.")

@router.get("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
@check_roles(["User", "Admin"])
async def get_logged_in_user(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> UserResponse:
    logging.debug("Entered get_current_user")
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    data = UserResponseData.model_validate(current_user)
    return UserResponse(data=data, detail="User fetched successfully.")

@router.get("/users/admins", response_model=UserListResponse, status_code=status.HTTP_200_OK)
@check_roles(["Admin"])
async def get_admins(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> UserListResponse:
    admins = session.exec(select(User).join(User.roles).where(Role.name == "Admin")).all()
    data = [UserResponseData.model_validate(admin) for admin in admins]
    return UserListResponse(data=data, detail=f"{len(data)} admins fetched successfully." if len(data) != 1 else f"{len(data)} admin fetched successfully.")

@router.get("/users/users", response_model=UserListResponse, status_code=status.HTTP_200_OK)
@check_roles(["Admin"])
async def get_users(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> UserListResponse:
    users = session.exec(select(User).join(User.roles).where(Role.name == "User")).all()
    data = [UserResponseData.model_validate(user) for user in users]
    return UserListResponse(data=data, detail=f"{len(data)} users fetched successfully." if len(data) != 1 else f"{len(data)} user fetched successfully.")

@router.get("/users/{user_uuid:uuid}", response_model=UserResponse, status_code=status.HTTP_200_OK)
@check_roles(["Admin"])
async def get_specific_user(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, session: Session = Depends(get_db)) -> UserResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User fetched successfully.")

# Post Requests

@router.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Register"])
async def add_user(create_user_request: UserCreateReq, session: Session = Depends(get_db)) -> UserResponse:
    username = create_user_request.username
    if session.exec(select(User).where(User.username == username)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Username: {username} already exists.")
    user = User.model_validate(create_user_request.model_dump())
    user_role = session.exec(select(Role).where(Role.name == "User")).first()
    user.roles.append(user_role)
    session.add(user)
    print(type(user.uuid))
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="New User has been added.")

# Put Requests

@router.put("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["User", "Admin"])
@check_roles(["User", "Admin"])
async def update_logged_in_user(current_user: Annotated[User, Security(get_current_user)], update_user_request: UserPutReq, session: Session = Depends(get_db)) -> UserResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    for attr, value in update_user_request.model_dump().items():
        setattr(current_user, attr, value) 
    session.commit()
    session.refresh(current_user)
    data = UserResponseData.model_validate(current_user)
    return UserResponse(data=data, detail="User updated.")

@router.put("/users/{user_uuid:uuid}", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["Admin"])
@check_roles(["Admin"])
async def update_user(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, update_user_request: UserPutReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    for attr, value in update_user_request.model_dump().items():
        setattr(user, attr, value) 
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")

# Patch Requests

@router.patch("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["User", "Admin"])
@check_roles(["User", "Admin"])
async def patch_logged_in_user(current_user: Annotated[User, Security(get_current_user)], update_user_request: UserPatchReq, session: Session = Depends(get_db)) -> UserResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    for attr, value in update_user_request.model_dump(exclude_unset=True).items():
        setattr(current_user, attr, value) 
    session.commit()
    session.refresh(current_user)
    data = UserResponseData.model_validate(current_user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/{user_uuid:uuid}", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["Admin"])
@check_roles(["Admin"])
async def patch_user(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, update_user_request: UserPatchReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    for attr, value in update_user_request.model_dump(exclude_unset=True).items():
        setattr(user, attr, value) 
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/me/username", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["User", "Admin"])
@check_roles(["User", "Admin"])
async def patch_logged_in_user_username(current_user: Annotated[User, Security(get_current_user)], update_user_request: UserUsernamePatchReq, session: Session = Depends(get_db)) -> UserResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if session.exec(select(User).where(User.username == update_user_request.username)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Username: {update_user_request.username} already exists.")
    current_user.username = update_user_request.username
    session.commit()
    session.refresh(current_user)
    data = UserResponseData.model_validate(current_user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/{user_uuid:uuid}/username", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["Admin"])
@check_roles(["Admin"])
async def patch_user_username(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, update_user_request: UserUsernamePatchReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    if session.exec(select(User).where(User.username == update_user_request.username)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Username: {update_user_request.username} already exists.")
    user.username = update_user_request.username
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/me/password", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["User", "Admin"])
@check_roles(["User", "Admin"])
async def patch_logged_in_user_password(current_user: Annotated[User, Security(get_current_user)], update_user_request: UserPasswordPatchReq, session: Session = Depends(get_db)) -> UserResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    current_user.hashed_password = update_user_request.password
    session.commit()
    session.refresh(current_user)
    data = UserResponseData.model_validate(current_user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/{user_uuid:uuid}/password", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["Admin"])
@check_roles(["Admin"])
async def patch_user_password(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, update_user_request: UserPasswordPatchReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    user.hashed_password = update_user_request.password
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")

@router.patch("/users/{user_uuid:uuid}/role", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["Admin"])
@check_roles(["Admin"])
async def patch_user_role(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, update_user_request: UserRolePatchReq, session: Session = Depends(get_db)) -> UserResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    role = session.exec(select(Role).where(Role.name == update_user_request.role)).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role: {update_user_request.role} not found.")
    user.roles = [role]
    session.commit()
    session.refresh(user)
    data = UserResponseData.model_validate(user)
    return UserResponse(data=data, detail="User updated.")

# Delete Requests 

@router.delete("/users/{user_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"]) 
@check_roles(["Admin"])
async def delete_user(current_user: Annotated[User, Security(get_current_user)], user_uuid: UUID, session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    session.delete(user)
    session.commit()