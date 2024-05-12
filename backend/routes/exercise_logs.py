from uuid import UUID
from typing import Annotated
from functools import lru_cache

from fastapi import APIRouter, HTTPException, status, Depends, Security
from sqlmodel import Session, select

from db import engine, get_db

from models.exercise_log import ExerciseLogCreateReq, ExerciseLogPatchReq

from models.responses import ExerciseLogResponseData, ExerciseLogResponse, ExerciseLogListResponse, ExerciseResponseData
from models.relationship_merge import Exercise, ExerciseLog, User
from utilities.authorization import check_roles, get_current_user


router = APIRouter()

@lru_cache(maxsize=128)
def get_all_exercise_logs_cached(current_user: User) -> list[ExerciseLogResponseData]:
    with Session(engine) as session:
        exercise_logs = session.exec(select(ExerciseLog).where(ExerciseLog.user_id == current_user.id)).all()
        data = []
        for exercise_log in exercise_logs:
            exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
            data.append(ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": current_user.uuid}))
        return data

@router.get("/exercise_logs", response_model=ExerciseLogListResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def get_all_exercise_logs(current_user: Annotated[User, Security(get_current_user)], session: Session = Depends(get_db)) -> ExerciseLogListResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    data = get_all_exercise_logs_cached(current_user)
    return ExerciseLogListResponse(data=data, detail="Exercise Logs fetched successfully.")

@router.get("/exercise_logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def get_specific_exercise_log(current_user: Annotated[User, Security(get_current_user)], exercise_log_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid).where(ExerciseLog.user_id == current_user.id)).first()
    if exercise_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} does not exist for user UUID: {current_user.uuid}.")
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": current_user.uuid})
    return ExerciseLogResponse(data=data, detail="Exercise log fetched successfully.")

@router.post("/exercise_logs", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
@check_roles(["User"])
async def create_exercise_log(current_user: Annotated[User, Security(get_current_user)], create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise = session.exec(select(Exercise).where(Exercise.uuid == create_exercise_log_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {create_exercise_log_request.exercise_uuid} not found.")
    exercise_log = ExerciseLog.model_validate(create_exercise_log_request.model_dump())
    exercise_log.user = current_user
    exercise_log.exercise = exercise
    session.add(exercise_log)
    session.commit()
    session.refresh(exercise_log)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data})
    get_all_exercise_logs_cached.cache_clear()
    return ExerciseLogResponse(data=data, detail="Exercise log created successfully.")

@router.put("/exercise_logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def update_exercise_log(current_user: Annotated[User, Security(get_current_user)], exercise_log_uuid: UUID, create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid).where(ExerciseLog.user_id == current_user.id)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == create_exercise_log_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {create_exercise_log_request.exercise_uuid} not found.")
    for attr, value in create_exercise_log_request.model_dump(exclude={"exercise_uuid"}).items():
        setattr(exercise_log, attr, value)
    exercise_log.exercise = exercise
    session.commit()
    session.refresh(exercise_log)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data})
    get_all_exercise_logs_cached.cache_clear()
    return ExerciseLogResponse(data=data, detail="Exercise log updated successfully.")

@router.patch("/exercise_logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK, tags=["User"])
@check_roles(["User"])
async def patch_exercise_log(current_user: Annotated[User, Security(get_current_user)], exercise_log_uuid: UUID, patch_exercise_log_request: ExerciseLogPatchReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    if patch_exercise_log_request.exercise_uuid:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == patch_exercise_log_request.exercise_uuid)).first()
        if not exercise: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {patch_exercise_log_request.exercise_uuid} not found.")
        exercise_log.exercise = exercise
    for attr, value in patch_exercise_log_request.model_dump(exclude_unset=True, exclude={"exercise_uuid"}).items():
        setattr(exercise_log, attr, value)
    session.commit()
    session.refresh(exercise_log)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data})
    get_all_exercise_logs_cached.cache_clear()
    return ExerciseLogResponse(data=data, detail="Exercise log updated successfully.")

@router.delete("/exercise_logs/{exercise_log_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
@check_roles(["User"])
async def delete_exercise_log(current_user: Annotated[User, Security(get_current_user)], exercise_log_uuid: UUID, session: Session = Depends(get_db)):
    current_user = session.exec(select(User).where(User.id == current_user.id)).first()
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise Log UUID: {exercise_log_uuid} not found.")
    session.delete(exercise_log)
    session.commit()
    get_all_exercise_logs_cached.cache_clear()