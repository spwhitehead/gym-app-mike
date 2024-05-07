from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from db import engine, get_db
from models.workout_exercise import WorkoutExerciseCreateReq, WorkoutExercisePatchReq
from models.responses import WorkoutExerciseResponseData, WorkoutExerciseResponse, WorkoutExerciseListResponse, ExerciseResponseData
from models.relationship_merge import WorkoutExercise, User, Exercise

router = APIRouter()

#Workout Exercises End Points
@router.get("/users/{user_uuid:uuid}/workout-exercises", response_model=WorkoutExerciseListResponse, status_code=status.HTTP_200_OK)
async def get_workout_exercises(user_uuid: UUID, session: Session = Depends(get_db)) -> WorkoutExerciseListResponse:
    if not session.exec(select(User).where(User.uuid == user_uuid)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout_exercises = session.exec(select(WorkoutExercise).where(WorkoutExercise.user_uuid == user_uuid)).all()
    data = []
    for workout_exercise in workout_exercises:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
        exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
        data.append(WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data}))
    return WorkoutExerciseListResponse(data=data, detail=f"{len(data)} workout exercises fetched successfully." if len(data) != 1 else f"{len(data)} workout exercise fetched successfully.")

@router.get("/users/{user_uuid:uuid}/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK)
async def get_workout_exercise(user_uuid: UUID, workout_exercise_uuid: UUID, session: Session = Depends(get_db)) -> WorkoutExerciseResponse:
    if not session.exec(select(User).where(User.uuid == user_uuid)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid and WorkoutExercise.user_uuid == user_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data})
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise fetched successfully.")

@router.post("/users/{user_uuid:uuid}/workout-exercises", response_model=WorkoutExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_workout_exercise(user_uuid: UUID, workout_exercise_request: WorkoutExerciseCreateReq, session: Session = Depends(get_db)) -> WorkoutExerciseResponse:
    if not session.exec(select(User).where(User.uuid == user_uuid)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise_request.exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {workout_exercise_request.exercise_uuid} not found.")
    workout_exercise = WorkoutExercise.model_validate(workout_exercise_request.model_dump(), update={"user_uuid": user_uuid})
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    session.refresh(exercise)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data})
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise added successfully.")

@router.patch("/users/{user_uuid:uuid}/workout-exercises/{workout_exercise_uuid}", response_model=WorkoutExerciseResponse, status_code=status.HTTP_200_OK)
async def update_workout_exercise(user_uuid: UUID, workout_exercise_uuid: UUID, workout_exercise_request: WorkoutExercisePatchReq, session: Session = Depends(get_db)):
    if not session.exec(select(User).where(User.uuid == user_uuid)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid and WorkoutExercise.user_uuid == user_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    if workout_exercise_request.exercise_uuid:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise_request.exercise_uuid)).first() 
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {workout_exercise_request.exercise_uuid} not found.")
    else:
        exercise = session.exec(select(Exercise).where(Exercise.uuid == workout_exercise.exercise_uuid)).first()
    for attr, value in workout_exercise_request.model_dump(exclude_unset=True).items():
        setattr(workout_exercise, attr, value)
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    exercise_data = ExerciseResponseData.model_validate(ExerciseResponseData.from_orm(exercise))
    data = WorkoutExerciseResponseData.model_validate(workout_exercise, update={"exercise":exercise_data})
    return WorkoutExerciseResponse(data=data, detail="Workout Exercise updated successfully.")

@router.delete("/users/{user_uuid:uuid}/workout-exercises/{workout_exercise_uuid}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_workout_exercise(user_uuid: UUID, workout_exercise_uuid: UUID, session: Session = Depends(get_db)):
    if not session.exec(select(User).where(User.uuid == user_uuid)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(WorkoutExercise).where(WorkoutExercise.uuid == workout_exercise_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout Exercise UUID: {workout_exercise_uuid} not found.")
    session.delete(workout)
    session.commit()