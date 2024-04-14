from uuid import uuid4 as new_uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine
from models.exercise import WorkoutExercise, Exercise
from models.requests import CreateWorkoutExerciseRequest, UpdateWorkoutExerciseRequest
from models.responses import ResponseWorkoutExercise, ResponseWorkoutExerciseList, WorkoutExerciseData, ExerciseData

router = APIRouter()

#Workout Exercises End Points
@router.get("/workout-exercises", response_model=ResponseWorkoutExerciseList, status_code=status.HTTP_200_OK)
async def get_workout_exercises() -> ResponseWorkoutExerciseList:
    with Session(bind=engine) as session:
        workout_exercises = session.exec(select(WorkoutExercise)).all()
        data = []
        for workout_exercise in workout_exercises:
            exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
            data.append(WorkoutExerciseData(**workout_exercise.model_dump(exclude={"exercise"}), exercise=ExerciseData(**exercise.model_dump(exclude={"target_muscles"}), target_muscles=[muscle.musclegroup for muscle in exercise.target_muscles])))
        return ResponseWorkoutExerciseList(data=data, detail="Workout Exercises fetched successfully.")

@router.get("/workout-exercises/{workout_exercise_uuid}", response_model=ResponseWorkoutExercise, status_code=status.HTTP_200_OK)
async def get_workout_exercise(workout_exercise_uuid: UUID) -> ResponseWorkoutExercise:
    with Session(bind=engine) as session:
        workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
        if not workout_exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
        data = WorkoutExerciseData(**workout_exercise.model_dump(exclude={"exercise"}), exercise=ExerciseData(**exercise.model_dump(exclude={"target_muscles"}), target_muscles=[muscle.musclegroup for muscle in exercise.target_muscles]))
        return ResponseWorkoutExercise(data=data, detail="Workout Exercise fetched successfully.")

@router.post("/workout-exercises", response_model=ResponseWorkoutExercise, status_code=status.HTTP_201_CREATED)
async def add_workout_exercise(workout_exercise_request: CreateWorkoutExerciseRequest) -> ResponseWorkoutExercise:
    with Session(bind=engine) as session:
        uuid = new_uuid()
        workout_exercise = WorkoutExercise(uuid=uuid, **workout_exercise_request.model_dump())
        workout_exercise.exercise_uuid = str(workout_exercise.exercise_uuid)
        session.add(workout_exercise)
        session.commit()
        workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == uuid)).first()
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
        data = WorkoutExerciseData(**workout_exercise.model_dump(exclude="exercise"), exercise=ExerciseData(**exercise.model_dump(exclude={"target_muscles"}), target_muscles=[muscle.musclegroup for muscle in exercise.target_muscles]))
        return ResponseWorkoutExercise(data=data, detail="Workout Exercise added successfully.")