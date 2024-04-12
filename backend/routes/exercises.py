from uuid import uuid4 as new_uuid
from uuid import UUID 

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, insert, delete, update

from db import engine, SQLModel

from models.models import (
    Exercise,
    SingleWorkout,
    WorkoutPlan,
    CreateWorkoutPlanRequest,
    UpdateWorkoutPlanRequest,
    User,
    ResistanceBand,
    MuscleGroup,
    BandColor,
    Gender,
    WeightUnits,
    HeightUnits,
    ResistenceType,
)

router = APIRouter()


# Exercises
@router.get("/exercises")
async def get_exercises():
    with Session(bind=engine) as session:
        exercises = session.exec(select(Exercise)).all()
        return exercises

@router.get("/exercises/{exercise_id}")
async def get_exercise(exercise_id: UUID):
    with Session(bind=engine) as session:
        exercise = session.exec(select(Exercise).where(Exercise.id == exercise_id)).first()
        if not exercise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise ID: {exercise_id} not found.")