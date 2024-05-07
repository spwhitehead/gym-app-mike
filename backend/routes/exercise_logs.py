from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from db import engine, get_db

from models.exercise_log import ExerciseLogCreateReq, ExerciseLogPatchReq

from models.responses import ExerciseLogResponseData, ExerciseLogResponse, ExerciseLogListResponse, ExerciseResponseData
from models.relationship_merge import Exercise, ExerciseLog, User


router = APIRouter()

# Exercise Logs

@router.get("/users/{user_uuid:uuid}/exercise_logs", response_model=ExerciseLogListResponse, status_code=status.HTTP_200_OK)
async def get_exercise_logs(user_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseLogListResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    exercise_logs = session.exec(select(ExerciseLog).where(ExerciseLog.user_id == user.id)).all()
    data = []
    for exercise_log in exercise_logs:
        exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
        data.append(ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": user_uuid}))
    return ExerciseLogListResponse(data=data, detail="Exercise Logs fetched successfully.")

@router.get("/users/{user_uuid:uuid}/exercise_logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def get_exercise_log(user_uuid: UUID, exercise_log_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if user is None:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if exercise_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} does not exist for user UUID: {user_uuid}.")
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": user_uuid})
    return ExerciseLogResponse(data=data, detail="Exercise log fetched successfully.")

@router.post("/users/{user_uuid:uuid}/exercise_logs", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_log(user_uuid: UUID, create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == create_exercise_log_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {create_exercise_log_request.exercise_uuid} not found.")
    exercise_log = ExerciseLog.model_validate(create_exercise_log_request.model_dump(), update={"user_uuid": user_uuid})
    exercise_log.exercise = exercise
    exercise_log.user_id = user.id
    exercise_log.exercise_id = exercise.id
    session.add(exercise_log)
    session.commit()
    session.refresh(exercise_log)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": user_uuid})
    return ExerciseLogResponse(data=data, detail="Exercise log created successfully.")

@router.put("/users/{user_uuid:uuid}/exercise_logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def update_exercise_log(user_uuid: UUID, exercise_log_uuid: UUID, create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == create_exercise_log_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {create_exercise_log_request.exercise_uuid} not found.")
    for attr, value in create_exercise_log_request.model_dump(exclude={"exercise_uuid"}).items():
        setattr(exercise_log, attr, value)
    exercise_log.exercise = exercise
    exercise_log.exercise_id = exercise.id
    session.commit()
    session.refresh(exercise_log)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": user_uuid})
    return ExerciseLogResponse(data=data, detail="Exercise log updated successfully.")

@router.patch("/users/{user_uuid:uuid}/exercise_logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def patch_exercise_log(user_uuid: UUID, exercise_log_uuid: UUID, patch_exercise_log_request: ExerciseLogPatchReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    if patch_exercise_log_request.exercise_uuid:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == patch_exercise_log_request.exercise_uuid)).first()
        if not exercise: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {patch_exercise_log_request.exercise_uuid} not found.")
        exercise_log.exercise = exercise
        exercise_log.exercise_id = exercise.id
    for attr, value in patch_exercise_log_request.model_dump(exclude_unset=True, exclude={"exercise_uuid"}).items():
        setattr(exercise_log, attr, value)
    session.commit()
    session.refresh(exercise_log)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise_log.exercise))
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_data, "user_uuid": user_uuid})
    return ExerciseLogResponse(data=data, detail="Exercise log updated successfully.")

@router.delete("/users/{user_uuid}/exercise_logs/{exercise_log_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_log(exercise_log_uuid: UUID, session: Session = Depends(get_db)):
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise Log UUID: {exercise_log_uuid} not found.")
    session.delete(exercise_log)
    session.commit()