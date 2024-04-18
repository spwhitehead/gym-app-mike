from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, insert, delete, update, text


from db import engine, get_db

from models.exercise import (
    Exercise,
    ExerciseMuscleLink,
    ExerciseCreateReq, ExerciseUpdateReq,
    ExerciseResponse, ExerciseListResponse, ExerciseResponseData
)
from models.workout_exercise import WorkoutExercise

router = APIRouter()

# Exercises
@router.get("/exercises", response_model=ExerciseListResponse, status_code=status.HTTP_200_OK)
async def get_exercises(session: Session = Depends(get_db)) -> ExerciseListResponse:
    exercises = session.exec(select(Exercise)).all()
    data = [ExerciseResponseData.model_validate(exercise) for exercise in exercises]
    return ExerciseListResponse(data=data, detail="Exercises fetched successfully.")

@router.get("/exercises/{exercise_uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK)
async def get_exercise(exercise_uuid: str, session: Session = Depends(get_db)):
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise ID: {exercise_uuid} not found.")
    data = ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail="Exercise fetched successfully.")

@router.post("/exercises/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_exercise(exercise_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = Exercise.model_validate(exercise_request.model_dump())
    exercise.target_muscles = [ExerciseMuscleLink(musclegroup=mg) for mg in exercise_request.target_muscles]
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise added successfully.")
            
@router.put("/exercises/{exercise_uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK) 
async def update_exercise(exercise_uuid: str, exercise_request: ExerciseUpdateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    for attr,value in exercise_request.model_dump(exclude_unset=True, exclude={"target_muscles"}).items():
        setattr(exercise, attr, value)
    if exercise_request.target_muscles is not None:
        exercise.target_muscles.clear()
        exercise.target_muscles.extend(
            [ExerciseMuscleLink(musclegroup=mg) for mg in exercise_request.target_muscles]
        )
    session.commit()
    session.refresh(exercise)
    data =  ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise updated successfully.")

@router.delete("/exercises/{exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_uuid: str, session: Session = Depends(get_db)):
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    session.exec(delete(WorkoutExercise).where(WorkoutExercise.exercise_uuid == exercise_uuid))
    session.exec(delete(Exercise).where(Exercise.uuid == exercise_uuid))
    session.commit()