
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, delete
from sqlalchemy.orm import selectinload


from db import engine, get_db

from models.exercise import (
    Exercise,
    ExerciseCreateReq, ExercisePatchReq,
    ExerciseResponse, ExerciseListResponse, ExerciseResponseData
)
from models.exercise_specific_muscle_link import ExerciseSpecificMuscleLink
from models.workout_exercise import WorkoutExercise
from models.unique_data import WorkoutCategory, MovementCategory, MajorMuscle, SpecificMuscle, Equipment

router = APIRouter()

# Exercises
@router.get("/exercises", response_model=ExerciseListResponse, status_code=status.HTTP_200_OK)
async def get_exercises(session: Session = Depends(get_db)) -> ExerciseListResponse:
    exercises = session.exec(select(Exercise)).all()
    data = [ExerciseResponseData.from_orm(exercise) for exercise in exercises]
    return ExerciseListResponse(data=data, detail="Exercises fetched successfully.")


@router.get("/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK)
async def get_exercise(exercise_uuid: UUID, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    data = ExerciseResponseData.from_orm(exercise)
    return ExerciseResponse(data=data, detail="Exercise fetched successfully.")


@router.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def add_exercise(exercise_post_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    workout_category_id, movement_category_id, major_muscle_id, equipment_id = session.exec(select(WorkoutCategory.id, MovementCategory.id, MajorMuscle.id, Equipment.id).where(
        WorkoutCategory.name == exercise_post_request.workout_category, 
        MovementCategory.name == exercise_post_request.movement_category, 
        MajorMuscle.name == exercise_post_request.major_muscle,
        Equipment.name == exercise_post_request.equipment
        )).first()
    if not workout_category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout category '{exercise_post_request.workout_category}' is not a valid option.")
    if not movement_category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movement category '{exercise_post_request.movement_category}' is not a valid option.")
    if not major_muscle_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Major muscle '{exercise_post_request.major_muscle}' is not a valid option.")
    if not equipment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Equipment '{exercise_post_request.equipment}' is not a valid option.")
    for specific_muscle in exercise_post_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        if not specific_muscle_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specific Muscle '{specific_muscle}' is not a valid option.")
    exercise = Exercise.model_validate(exercise_post_request.model_dump(
        exclude={"specific_muscles"}),
        update={"workout_category_id":workout_category_id,
                "movement_category_id": movement_category_id,
                "major_muscle_id": major_muscle_id,
                "equipment_id":equipment_id
                }
        )
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    for specific_muscle in exercise_post_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        session.add(ExerciseSpecificMuscleLink(exercise_id=exercise.id, specific_muscle_id=specific_muscle_id))
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.from_orm(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise added successfully.")
            

@router.put("/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK) 
async def update_exercise(exercise_uuid: UUID, exercise_put_request: ExerciseCreateReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    for attr,value in exercise_put_request.model_dump(exclude={"workout_category", "movement_category", "equipment", "major_muscle","specific_muscles"}).items():
        setattr(exercise, attr, value)
    workout_category_id, movement_category_id, major_muscle_id, equipment_id = session.exec(select(WorkoutCategory.id, MovementCategory.id, MajorMuscle.id, Equipment.id).where(
        WorkoutCategory.name == exercise_put_request.workout_category, 
        MovementCategory.name == exercise_put_request.movement_category, 
        MajorMuscle.name == exercise_put_request.major_muscle,
        Equipment.name == exercise_put_request.equipment
        )).first()
    if not workout_category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout category '{exercise_put_request.workout_category}' is not a valid option.")
    if not movement_category_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movement category '{exercise_put_request.movement_category}' is not a valid option.")
    if not major_muscle_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Major muscle '{exercise_put_request.major_muscle}' is not a valid option.")
    if not equipment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Equipment '{exercise_put_request.equipment}' is not a valid option.")
    exercise.workout_category_id = workout_category_id
    exercise.movement_category_id = movement_category_id
    exercise.major_muscle_id = major_muscle_id
    exercise.equipment_id = equipment_id
    for specific_muscle in exercise_put_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        if not specific_muscle_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specific Muscle '{specific_muscle}' is not a valid option.")
    exercise.specific_muscles.clear()
    for specific_muscle in exercise_put_request.specific_muscles:
        specific_muscle_id = session.exec(select(SpecificMuscle.id).where(SpecificMuscle.name == specific_muscle)).first()
        session.add(ExerciseSpecificMuscleLink(specific_muscle_id=specific_muscle_id, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data =  ExerciseResponseData.from_orm(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise updated successfully.")

@router.patch("/exercises/{exercise_uuid:uuid}", response_model=ExerciseResponse, status_code=status.HTTP_200_OK)
async def update_exercise(exercise_uuid: UUID, exercise_patch_request: ExercisePatchReq, session: Session = Depends(get_db)) -> ExerciseResponse:
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    with session.no_autoflush:
        for attr, value in exercise_patch_request.model_dump(exclude_unset=True).items():
            match attr:
                case "name":
                    setattr(exercise, attr, value)
                case "description":
                    setattr(exercise, attr, value)
                case "workout_category":
                    workout_category_id = session.exec(select(WorkoutCategory).where(WorkoutCategory.name == value)).first().id
                    if not workout_category_id:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workout category '{value}' is not a valid option.")
                    exercise.workout_category_id = workout_category_id
                case "movement_category":
                    movement_category_id = session.exec(select(MovementCategory).where(MovementCategory.name == value)).first().id
                    if not movement_category_id:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movement category '{value}' is not a valid option.")
                    exercise.movement_category_id = movement_category_id
                case "major_muscle":
                    major_muscle_id = session.exec(select(MajorMuscle).where(MajorMuscle.name == value)).first().id
                    if not major_muscle_id:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Major muscle '{value}' is not a valid option.")
                    exercise.major_muscle_id = major_muscle_id
                case "equipment":
                    equipment_id = session.exec(select(Equipment).where(Equipment.name == value)).first().id
                    if not equipment_id:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Equipment '{value}' is not a valid option.")
                    exercise.equipment_id = equipment_id
                case "specific_muscles":
                    specific_muscle_ids =[]
                    for specific_muscle in value:
                        specific_muscle_id = session.exec(select(SpecificMuscle).where(SpecificMuscle.name == specific_muscle)).first().id
                        if not specific_muscle_id:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specific muscle '{value}' is not a valid option.")
                        specific_muscle_ids.append(specific_muscle_id)
                    exercise.specific_muscles.clear()
                    for specific_muscle_id in specific_muscle_ids:
                        session.add(ExerciseSpecificMuscleLink(specific_muscle_id=specific_muscle_id, exercise_id=exercise.id))
    session.commit()
    session.refresh(exercise)
    data = ExerciseResponseData.from_orm(exercise)
    return ExerciseResponse(data=data, detail=f"Exercise patched successfully.")

@router.delete("/exercises/{exercise_uuid:uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(exercise_uuid: UUID, session: Session = Depends(get_db)):
    exercise = session.exec(select(Exercise).where(Exercise.uuid == exercise_uuid)).first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise UUID: {exercise_uuid} not found.")
    session.delete(exercise)
    session.commit()