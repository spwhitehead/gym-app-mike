from uuid import uuid4 as new_uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, insert, delete, update

from db import engine, get_db
from models.exercise import Exercise, ExerciseResponseData
from models.workout_exercise import (
    WorkoutExercise, 
    WorkoutExerciseCreateReq, WorkoutExerciseUpdateReq,
    WorkoutExerciseResponseData,
    WorkoutExerciseResponse, WorkoutExerciseListResponse
)

router = APIRouter()

#Workout Exercises End Points
@router.get("/workout-exercises", response_model=WorkoutExerciseListResponse, status_code=status.HTTP_200_OK)
async def get_workout_exercises(session: Session = Depends(get_db)) -> WorkoutExerciseListResponse:
    workout_exercises = session.exec(select(WorkoutExercise)).all()
    data = []
    for workout_exercise in workout_exercises:
        print(workout_exercise)
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
        exercise_data = ExerciseResponseData.model_validate(exercise)
        data.append(WorkoutExerciseResponseData.model_validate(workout_exercise, update={"name":exercise_data.name, "description":exercise_data.description, "target_muscles":exercise_data.target_muscles}))
    print(data)
    return WorkoutExerciseListResponse(data=data, detail="Workout Exercises fetched successfully.")

@router.get("/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK)
async def get_workout_exercise(workout_exercise_uuid: str, session: Session = Depends(get_db)) -> WorkoutExerciseResponse:
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
    exercise_data = ExerciseResponseData.model_validate(exercise)
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"name":exercise_data.name, "description":exercise_data.description, "target_muscles":exercise_data.target_muscles})
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise fetched successfully.")

@router.post("/workout-exercises", response_model=WorkoutExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_workout_exercise(workout_exercise_request: WorkoutExerciseCreateReq, session: Session = Depends(get_db)) -> WorkoutExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == str(workout_exercise_request.exercise_uuid))).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {workout_exercise_request.exercise_uuid} not found.")
    workout_exercise = WorkoutExercise.model_validate(workout_exercise_request.model_dump())
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    session.refresh(exercise)
    exercise_data = ExerciseResponseData.model_validate(exercise)
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"name":exercise_data.name, "description":exercise_data.description, "target_muscles":exercise_data.target_muscles})
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise added successfully.")

@router.put("/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK)
async def update_workout_exercise(workout_exercise_uuid: str, workout_exercise_request: WorkoutExerciseUpdateReq):
    with Session(bind=engine) as session:
        workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
        if not workout_exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
        session.exec(update(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid).values(
            exercise_uuid = str(workout_exercise_request.exercise_uuid) if workout_exercise_request.exercise_uuid is not None else WorkoutExercise.exercise_uuid,
            sets = workout_exercise_request.sets if workout_exercise_request.sets is not None else WorkoutExercise.sets,
            reps = workout_exercise_request.reps if workout_exercise_request.reps is not None else WorkoutExercise.reps,
            resistance_type = workout_exercise_request.resistance_type if workout_exercise_request.resistance_type is not None else WorkoutExercise.resistance_type,
            resistance_weight = workout_exercise_request.resistance_weight if workout_exercise_request.resistance_weight is not None else WorkoutExercise.resistance_weight
        ))
        session.commit()
        session.refresh(workout_exercise)
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
        data = WorkoutExerciseResponseData(**workout_exercise.model_dump(exclude="exercise"), exercise=ExerciseResponseData(**exercise.model_dump(exclude={"target_muscles"}), target_muscles=[muscle.musclegroup for muscle in exercise.target_muscles]))
        return WorkoutExerciseResponse(data=data, detail="Workout Exercise updated successfully.")

@router.delete("/workout-exercises/{workout_exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_workout_exercise(workout_exercise_uuid: str):
    with Session(bind=engine) as session:
        workout = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
        if not workout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
        session.exec(delete(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid))
        session.commit()