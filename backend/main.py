from fastapi import FastAPI

from db import engine, SQLModel
from routes import exercises, users, workouts

app = FastAPI()

app.include_router(workouts.router, tags=["Workouts"]) 
app.include_router(users.router, tags=["Users"])
app.include_router(exercises.router, tags=["Exercises"])
