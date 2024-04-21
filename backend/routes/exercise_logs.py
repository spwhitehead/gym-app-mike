from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, delete

from db import engine, get_db

from models.exercise_log import (
    ExerciseLog,
    ExerciseLogCreateReq, ExerciseLogUpdateReq,
    ExerciseLogResponseData,
    ExerciseLogResponse, ExerciseLogListResponse
)

from models.exercise import ExerciseResponseData, Exercise

router = APIRouter()

# Exercise Logs
@router.get("/exercise_logs", response_model=ExerciseLogListResponse, status_code=status.HTTP_200_OK)
async def get_exercise_logs(session: Session = Depends(get_db)) -> ExerciseLogListResponse:
    exercise_logs = session.exec(select(ExerciseLog)).all()
    data = [ExerciseLogResponseData.model_validate(exercise_log) for exercise_log in exercise_logs]
    return ExerciseLogListResponse(data=data, detail="Exercise Logs fetched successfully.")


@router.get("/exercise_logs/{exercise_log_uuid}", response_model=ExerciseLogResponse, status_code=status.HTTP_200_OK)
async def get_exercise_log(exercise_uuid: str, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    exercise_log = session.exec(select(ExerciseLog).where(ExerciseLog.uuid == exercise_uuid)).first()
    if not exercise_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise log UUID: {exercise_uuid} not found.")
    data = ExerciseLogResponseData.model_validate(exercise_log)
    return ExerciseLogResponse(data=data, detail="Exercise log fetched successfully.")

@router.post("/exercise_logs", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_log(create_exercise_log_request: ExerciseLogCreateReq, session: Session = Depends(get_db)) -> ExerciseLogResponse:
    exercise_log = ExerciseLog.model_validate(create_exercise_log_request.model_dump())
    exercise_log.exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_log.exercise_uuid)).first()
    session.add(exercise_log)
    session.commit()
    session.refresh(exercise_log)
    print(exercise_log)
    print(exercise_log.exercise)
    print(exercise_log.exercise_uuid)
    exercise_response_data = ExerciseResponseData.model_validate(exercise_log.exercise)
    data = ExerciseLogResponseData.model_validate(exercise_log, update={"exercise": exercise_response_data})
    return ExerciseLogResponse(data=data, detail="Exercise log created successfully.")