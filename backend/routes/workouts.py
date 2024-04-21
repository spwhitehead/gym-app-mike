from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, insert, delete, update 

from db import engine, get_db
from models.workout import Workout, WorkoutCreateReq, WorkoutUpdateReq, WorkoutAddWorkoutExerciseReq, WorkoutResponseData, WorkoutResponse, WorkoutListResponse
from models.exercise import Exercise, ExerciseResponseData
from models.workout_exercise import WorkoutExercise, WorkoutExerciseResponseData

router = APIRouter()

# Workout End Points
@router.get("/workouts", response_model=WorkoutListResponse, status_code=status.HTTP_200_OK)
async def get_workouts(session: Session = Depends(get_db)) -> WorkoutListResponse:
    workouts = session.exec(select(Workout)).all()
    data = [WorkoutResponseData.model_validate(workout) for workout in workouts]
    return WorkoutListResponse(data=data, detail="Workouts fetched successfully.")
    
@router.get("/workouts/{workout_uuid}", response_model=WorkoutResponse, status_code=status.HTTP_200_OK)
async def get_workout(workout_uuid: str, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout fetched successfully.")

@router.post("/workouts/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(workout_request: WorkoutCreateReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = Workout.model_validate(workout_request.model_dump())
    session.add(workout)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout added successfully.")

@router.put("/workouts/{workout_uuid}", response_model=WorkoutResponse, status_code=status.HTTP_200_OK)
async def update_workout(workout_uuid: str, workout_request: WorkoutUpdateReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.")
    for attr, value in workout_request.model_dump(exclude_unset=True).items():
        setattr(workout, attr, value)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout updated successfully.")

@router.post("/workouts/{workout_uuid}/exercises", response_model=WorkoutResponse, status_code=status.HTTP_200_OK)
async def link_workout_exercise_to_workout(workout_uuid: str, workout_add_workout_exercise_request: WorkoutAddWorkoutExerciseReq, session: Session = Depends(get_db)) -> WorkoutResponse:
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.") 
    workout_add_workout_exercise_request.workout_exercise_uuid = str(workout_add_workout_exercise_request.workout_exercise_uuid)
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_add_workout_exercise_request.workout_exercise_uuid)).first()
    if not workout_exercise:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout Exercise UUID: {workout_uuid} not found.") 
    workout.workout_exercises.append(workout_exercise)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Added workout exercise succesffully.")

@router.delete("/workouts/{workout_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(workout_uuid: str, session: Session = Depends(get_db)):
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    session.delete(workout)
    session.commit()

@router.delete("/workouts/{workout_uuid}/exercises/{workout_exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_workout_exercise_from_workout(workout_uuid: str, workout_exercise_uuid: str, session: Session = Depends(get_db)):
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.workout_id == workout.id and WorkoutExercise.uuid == workout_exercise_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_uuid} not found.")
    workout.workout_exercises.remove(workout_exercise)
    workout_exercise.workout_id = None
    session.commit()
    