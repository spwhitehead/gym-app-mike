
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, delete


from db import engine, get_db

from models.exercise import (
    Exercise,
    ExerciseSpecificMuscleLink,
    ExerciseCreateReq, ExercisePatchReq,
    ExerciseResponse, ExerciseListResponse, ExerciseResponseData
)
from models.workout_exercise import WorkoutExercise
from models.unique_data import WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment

router = APIRouter()

# Exercises
@router.get("/exercises", response_model=ExerciseListResponse, status_code=status.HTTP_200_OK)
async def get_exercises(session: Session = Depends(get_db)) -> ExerciseListResponse:
    exercises = session.exec(select(Exercise)).all()
    data = [ExerciseResponseData.model_validate(exercise,
                                                update={"workout_category": exercise.workout_category.name,
                                                        "movement_category": exercise.movement_category.name,
                                                        "major_muscle": exercise.major_muscle.name,
                                                        "equipment": exercise.equipment.name,
                                                        "specific_muscles": [specific_muscle_link.specific_muscle.name for specific_muscle_link in exercise.specific_muscles],
                                                        }) for exercise in exercises]
    return ExerciseListResponse(data=data, detail="Exercises fetched successfully.")

@router.get("/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK)
async def get_exercise(exercise_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    data = ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail="Exercise fetched successfully.")

@router.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_exercise(exercise_post_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    workout_category_id, movement_category_id, major_muscle_id, equipment_id = session.exec(select(WorkoutCategory.id, MovementCategory.id, MajorMuscle.id, Equipment.id).where(
        WorkoutCategory.name == exercise_post_request.workout_category, 
        MovementCategory.name == exercise_post_request.movement_category, 
        MajorMuscle.name == exercise_post_request.major_muscle,
        Equipment.name == exercise_post_request.equipment
        )).first()
    exercise = Exercise.model_validate(exercise_post_request.model_dump(),
                                       update={"workout_category_id":workout_category_id,
                                               "movement_category_id": movement_category_id,
                                               "major_muscle_id": major_muscle_id,
                                               "equipment_id":equipment_id
                                               })
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    for specific_muscle in exercise_post_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        session.add(ExerciseSpecificMuscleLink(exercise_id=exercise.id, specific_muscle_id=specific_muscle_id))
    session.commit()
    session.refresh(exercise)
    specific_muscles = [specific_muscle_link.specific_muscle.name for specific_muscle_link in exercise.specific_muscles]
    data = ExerciseResponseData.model_validate(exercise, update={"workout_category":exercise_post_request.workout_category, "movement_category": exercise_post_request.movement_category, "equipment":exercise_post_request.equipment, "major_muscle":exercise_post_request.major_muscle, "specific_muscles": specific_muscles})

    return ExerciseResponse(data=data, detail=f"Exercise added successfully.")
            
@router.put("/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK) 
async def update_exercise(exercise_uuid: UUID, exercise_put_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    for attr,value in exercise_put_request.model_dump(exclude={"major_muscles", "specific_muscles"}).items():
        setattr(exercise, attr, value)
    exercise.specific_muscles.clear()
    for specific_muscle in exercise_put_request.specific_muscles:
        session.add(ExerciseSpecificMuscleLink(specific_muscles=specific_muscle, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data =  ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise updated successfully.")

@router.patch("/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK)
async def update_exercise(exercise_uuid: UUID, exercise_patch_request: ExercisePatchReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    for attr, value in exercise_patch_request.model_dump(exclude_unset=True, exclude={"major_muscles", "specific_muscles"}).items():
        setattr(exercise, attr, value)
    if exercise_patch_request.specific_muscles is not None:
        exercise.specific_muscles.clear()
        for specific_muscle in exercise_patch_request.specific_muscles:
            session.add(ExerciseSpecificMuscleLink(specific_muscles=specific_muscle, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.model_validate(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise patched successfully.")

@router.delete("/exercises/{exercise_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_uuid: UUID, session: Session = Depends(get_db)):
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    session.exec(delete(WorkoutExercise).where(WorkoutExercise.exercise_uuid == exercise_uuid))
    session.exec(delete(Exercise).where(Exercise.uuid == exercise_uuid))
    session.commit()