from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine
from models.workout import Workout
from models.requests import CreateWorkoutRequest, UpdateWorkoutRequest
from models.responses import ResponseWorkout, ResponseWorkoutList, WorkoutData

router = APIRouter()

# Workout End Points
@router.get("/workouts", response_model=ResponseWorkoutList, status_code=status.HTTP_200_OK)
async def get_workouts() -> ResponseWorkoutList:
    with Session(bind=engine) as session:
        workouts = session.exec(select(Workout)).all()
        data = [WorkoutData(**workout.model_dump()) for workout in workouts]
        return ResponseWorkoutList(data=data, detail="Workouts fetched successfully.")
    
@router.get("/workouts/{workout_uuid}", response_model=ResponseWorkout, status_code=status.HTTP_200_OK)
async def get_workout(workout_uuid: UUID) -> ResponseWorkout:
    with Session(bind=engine) as session:
        workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
        if not workout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
        data = WorkoutData(**workout.model_dump())
        return ResponseWorkout(data=data, detail="Workout fetched successfully.")

@router.post("/workouts/", response_model=ResponseWorkout, status_code=status.HTTP_201_CREATED)
async def add_workout(workout_request: CreateWorkoutRequest) -> ResponseWorkout:
    with Session(bind=engine) as session:
        uuid = new_uuid()
        session.exec(insert(Workout).values(uuid=uuid, **workout_request.model_dump()))
        session.commit()
        workout = session.exec(select(Workout).where(Workout.uuid == uuid)).first()
        data = WorkoutData(**workout.model_dump())
        return ResponseWorkout(data=data, detail="Workout added successfully.")

@router.put("/workouts/{workout_uuid}", response_model=ResponseWorkout, status_code=status.HTTP_200_OK)
async def update_workout(workout_uuid: UUID, workout_request: UpdateWorkoutRequest) -> ResponseWorkout:
    with Session(bind=engine) as session:
        workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
        if not workout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.")
        session.exec(update(Workout).where(Workout.uuid == workout_uuid).values(
            name=workout_request.name if workout_request.name is not None else Workout.name,
            description=workout_request.name if workout_request.name is not None else Workout.name))
        session.commit() 
        session.refresh(workout)
        data = WorkoutData(**workout.model_dump())
        return ResponseWorkout(data=data, detail="Workout updated.")

@router.delete("/workouts/{workout_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(workout_uuid: UUID):
    with Session(bind=engine) as session:
        workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
        if not workout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
        session.exec(delete(Workout).where(Workout.uuid == workout_uuid))
        session.commit()