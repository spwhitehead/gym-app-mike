from uuid import uuid4 as new_uuid
from uuid import UUID

from fastapi import FastAPI, HTTPException, status, APIRouter
from sqlmodel import Session, select, insert, delete

from db import engine, SQLModel
from routes import workout_plans, exercises
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


app = FastAPI()
app.include_router(workout_plans.router) 
app.include_router(exercises.router)
# Exercises

# @router.get("/exercises")

# @router.post("/exercises")
# @router.update("/exercises/{exercise_id}")
# @router.delete("/exercises/{exercise_id}")

# @router.get("/exercises/{exercise_id}")
# 
# @router.get("/users")
# 
# @router.get("/users/{user_id}")
# 
# @router.get("/settings")