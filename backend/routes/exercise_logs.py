from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, delete

from db import engine, get_db

from models.exercise_log import (
    ExerciseLog,
    ExerciseLogCreateReq, ExerciseLogPatchReq,
    ExerciseLogResponseData,
    ExerciseLogResponse, ExerciseLogListResponse
)

from models.exercise import ExerciseResponseData, Exercise

router = APIRouter()

# Exercise Logs

@router.get("/exercises/logs", response_model=ExerciseLogListResponse, status_code=status.HTTP_200_OK)
async def get_exercise_logs(session: Session = Depends(get_db)) -> ExerciseLogListResponse:
    exercise_logs = session.exec(select(ExerciseLog)).all()
    data = [ExerciseLogResponseData.model_validate(exercise_log) for exercise_log in exercise_logs]
    return ExerciseLogListResponse(data=data, detail="Exercise Logs fetched successfully.")

@router.get("/exercises/logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def get_exercise_log(exercise_log_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    data = ExerciseLogResponseData.model_validate(exercise_log)
    return ExerciseLogResponse(data=data, detail=f"Exercise log fetched successfully.")

@router.post("/exercises/logs", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_log(create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    exercise_log = ExerciseLog.model_validate(create_exercise_log_request.model_dump())
    exercise_log.exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_log.exercise_uuid)).first()
    session.add(exercise_log)
    session.commit()
    session.refresh(exercise_log)
    exercise_response_data = ExerciseResponseData.model_validate(exercise_log.exercise)
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_response_data})
    return ExerciseLogResponse(data=data, detail="Exercise log created successfully.")

@router.put("/exercises/logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def update_exercise_log(exercise_log_uuid: UUID, create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    if not session.exec(select(Exercise).where(Exercise.uuid == create_exercise_log_request.exercise_uuid)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {create_exercise_log_request.exercise_uuid} not found.")
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    for attr, value in create_exercise_log_request.model_dump().items():
        setattr(exercise_log, attr, value)
    session.commit()
    session.refresh(exercise_log)
    exercise_response_data = ExerciseResponseData.model_validate(exercise_log.exercise)
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_response_data})
    return ExerciseLogResponse(data=data, detail="Exercise log updated successfully.")

@router.patch("/exercises/logs/{exercise_log_uuid:uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def patch_exercise_log(exercise_log_uuid: UUID, patch_exercise_log_request: ExerciseLogPatchReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_log_uuid} not found.")
    if patch_exercise_log_request.exercise_uuid:
        if not session.exec(select(Exercise).where(Exercise.uuid == patch_exercise_log_request.exercise_uuid)).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {patch_exercise_log_request.exercise_uuid} not found.")
    for attr, value in patch_exercise_log_request.model_dump(exclude_unset=True).items():
        setattr(exercise_log, attr, value)
    session.commit()
    session.refresh(exercise_log)
    exercise_response_data = ExerciseResponseData.model_validate(exercise_log.exercise)
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_response_data})
    return ExerciseLogResponse(data=data, detail="Exercise log updated successfully.")

@router.delete("/exercises/logs/{exercise_log_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_log(exercise_log_uuid: UUID, session: Session = Depends(get_db)):
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_log_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise Log UUID: {exercise_log_uuid} not found.")
    session.delete(exercise_log)
    session.commit()