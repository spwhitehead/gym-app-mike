from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, insert, delete, update 

from db import engine, get_db
from models.workout import (
    WorkoutCreateReq, WorkoutPatchReq, WorkoutAddWorkoutExerciseReq
)
from models.responses import (
    WorkoutResponseData, WorkoutResponse, WorkoutListResponse,
    ExerciseResponseData, WorkoutExerciseResponseData
)
from models.relationship_merge import (
    WorkoutExercise, Exercise, User, Workout
)

router = APIRouter()

# Workout End Points
@router.get("/users/{user_uuid:uuid}/workouts", 
            response_model=WorkoutListResponse, 
            status_code=status.HTTP_200_OK)
async def get_workouts(user_uuid: UUID, session: Session = Depends(get_db)) -> WorkoutListResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workouts: list[Workout] = session.exec(select(Workout).where(Workout.user_id == user.id)).all()
    data = [WorkoutResponseData.model_validate(workout) for workout in workouts]
    return WorkoutListResponse(data=data, 
                               detail=f"{len(workouts)} workouts fetched successfully." 
                               if len(workouts) != 1 
                               else f"{len(workouts)} workout fetched successfully.")
    
@router.get("/users/{user_uuid:uuid}/workouts/{workout_uuid:uuid}", 
            response_model=WorkoutResponse, 
            status_code=status.HTTP_200_OK)
async def get_workout(user_uuid: UUID, workout_uuid: UUID, 
                      session: Session = Depends(get_db)) -> WorkoutResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout fetched successfully.")

@router.post("/users/{user_uuid:uuid}/workouts", 
             response_model=WorkoutResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_workout(user_uuid: UUID, workout_request: WorkoutCreateReq, 
                         session: Session = Depends(get_db)) -> WorkoutResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = Workout.model_validate(workout_request.model_dump(), update={"user_id": user.id})
    session.add(workout)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout added successfully.")

@router.put("/users/{user_uuid:uuid}/workouts/{workout_uuid:uuid}", 
            response_model=WorkoutResponse, 
            status_code=status.HTTP_200_OK)
async def update_workout(user_uuid: UUID, workout_uuid: UUID, workout_request: WorkoutCreateReq, 
                         session: Session = Depends(get_db)) -> WorkoutResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.")
    for attr, value in workout_request.model_dump().items():
        setattr(workout, attr, value)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout updated successfully.")

@router.patch("/users/{user_uuid:uuid}/workouts/{workout_uuid:uuid}", 
              response_model=WorkoutResponse, 
              status_code=status.HTTP_200_OK)
async def patch_workout(user_uuid: UUID, workout_uuid: UUID, workout_request: WorkoutPatchReq, 
                        session: Session = Depends(get_db)) -> WorkoutResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.")
    for attr, value in workout_request.model_dump(exclude_unset=True).items():
        setattr(workout, attr, value)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Workout updated successfully.")

@router.delete("/users/{user_uuid:uuid}/workouts/{workout_uuid:uuid}", 
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(user_uuid: UUID, workout_uuid: UUID, 
                         session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    session.delete(workout)
    session.commit()


# Workout Exercise End Points
@router.post("/users/{user_uuid:uuid}/workouts/{workout_uuid:uuid}/workout_exercises", 
             response_model=WorkoutResponse, 
             status_code=status.HTTP_200_OK)
async def link_workout_exercise_to_workout(user_uuid: UUID, workout_uuid: UUID, 
                                           workout_add_workout_exercise_request: WorkoutAddWorkoutExerciseReq, 
                                           session: Session = Depends(get_db)) -> WorkoutResponse:
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Workout UUID: {workout_uuid} not found.") 
    workout_exercise = session.exec(select(WorkoutExercise)
                                    .where(WorkoutExercise.uuid == 
                                           workout_add_workout_exercise_request.workout_exercise_uuid)
                                    ).first()
    if not workout_exercise:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                           detail= f"Workout Exercise UUID: {workout_uuid} not found.") 
    workout_exercise.workout_id = workout.id
    workout.workout_exercises.append(workout_exercise)
    session.commit()
    session.refresh(workout)
    data = WorkoutResponseData.model_validate(workout)
    return WorkoutResponse(data=data, detail="Added workout exercise succesfully.")



@router.delete("/users/{user_uuid:uuid}/workouts/{workout_uuid:uuid}/exercises/{workout_exercise_uuid:uuid}", 
               status_code=status.HTTP_204_NO_CONTENT)
async def unlink_workout_exercise_from_workout(user_uuid: UUID, workout_uuid: UUID, 
                                               workout_exercise_uuid: UUID, 
                                               session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.uuid == user_uuid)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User UUID: {user_uuid} not found.")
    workout = session.exec(select(Workout).where(Workout.uuid == workout_uuid)).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout UUID: {workout_uuid} not found.")
    workout_exercise = session.exec(select(WorkoutExercise).where(WorkoutExercise.workout_id == workout.id and 
                                                                  WorkoutExercise.uuid == workout_exercise_uuid)).first()
    if not workout_exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Workout Exercise UUID: {workout_uuid} not found.")
    workout.workout_exercises.remove(workout_exercise)
    workout_exercise.workout_id = None
    session.commit()
    