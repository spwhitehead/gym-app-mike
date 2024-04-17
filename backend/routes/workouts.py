from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine
from models.exercise import Exercise, ExerciseResponseData
from models.workout_exercise import WorkoutExercise
from models.workout import Workout, WorkoutExerciseLink
from models.requests import CreateWorkoutRequest, UpdateWorkoutRequest, AddWorkoutExerciseRequest
from models.responses import ResponseWorkout, ResponseWorkoutList, WorkoutData, WorkoutExerciseData

router = APIRouter()

# Workout End Points
@router.get("/workouts", response_model=ResponseWorkoutList, status_code=status.HTTP_200_OK)
async def get_workouts() -> ResponseWorkoutList:
    workout_data_list = []
    with Session(bind=engine) as session:
        workouts = session.exec(select(Workout)).all()
        for workout in workouts:
            workout_exercise_links = session.exec(select(WorkoutExerciseLink).where(WorkoutExerciseLink.workout_id == workout.id)).all()
            workout_exercises_data = []
            for workout_exercise_link in workout_exercise_links:
                workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.id == workout_exercise_link.workout_exercise_id)).first()
                exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
                target_muscles = [muscle_link.musclegroup for muscle_link in exercise.target_muscles]
                exercise_data = ExerciseResponseData(**workout_exercise.model_dump(exclude={"target_muscles"}), target_muscles=target_muscles)
                workout_exercises_data.append(WorkoutExerciseData(**workout_exercise.model_dump(exclude={"exercise"}),exercise=exercise_data))
            workout_data = WorkoutData(**workout.model_dump(exclude={"workout_exercises"}), workout_exercises=workout_exercises_data)
            workout_data_list.append(workout_data)
        return ResponseWorkoutList(data=workout_data_list, detail="Workouts fetched successfully.")

    
@router.get("/workouts/{workout_uuid}", response_model=ResponseWorkout, status_code=status.HTTP_200_OK)
async def get_workout(workout_uuid: UUID) -> ResponseWorkout:
    with Session(bind=engine) as session:
        workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
        if not workout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
        workout_exercise_links = session.exec(select(WorkoutExerciseLink).where(WorkoutExerciseLink.workout_id == workout.id)).all()
        workout_exercises_data = []
        for workout_exercise_link in workout_exercise_links:
            workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.id == workout_exercise_link.workout_exercise_id)).first()
            exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first() 
            target_muscles = [muscle_link.musclegroup for muscle_link in exercise.target_muscles]
            exercise_data = ExerciseResponseData(**workout_exercise.model_dump(exclude={"target_muscles"}), target_muscles=target_muscles)
            workout_exercises_data.append(WorkoutExerciseData(**workout_exercise.model_dump(exclude={"exercise"}), exercise=exercise_data))
        data = WorkoutData(**workout.model_dump(exclude={"workout_exercises"}), workout_exercises=workout_exercises_data)
        return ResponseWorkout(data=data, detail="Workout fetched successfully.")


@router.post("/workouts/", response_model=ResponseWorkout, status_code=status.HTTP_201_CREATED)
async def create_workout(workout_request: CreateWorkoutRequest) -> ResponseWorkout:
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
        return ResponseWorkout(data=data, detail="Workout updated successfully.")

@router.put("/workouts/{workout_uuid}/add_exercise", response_model=ResponseWorkout, status_code=status.HTTP_200_OK)
async def add_workout_exercise(workout_uuid: UUID, add_workout_exercise_request: AddWorkoutExerciseRequest) -> ResponseWorkout:
    with Session(bind=engine) as session:
        workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
        workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == add_workout_exercise_request.workout_exercise_uuid)).first()
        session.exec(insert(WorkoutExerciseLink).values(workout_id=workout.id, workout_exercise_id=workout_exercise.id))
        session.commit()
        session.refresh(workout)
        session.refresh(workout_exercise)
        data = WorkoutData(**workout.model_dump())
        print(workout.exercises)
        return ResponseWorkout(data=data, detail="Workout Exercise added successfully.")


@router.delete("/workouts/{workout_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(workout_uuid: UUID):
    with Session(bind=engine) as session:
        workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
        if not workout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
        session.exec(delete(Workout).where(Workout.uuid == workout_uuid))
        session.commit()