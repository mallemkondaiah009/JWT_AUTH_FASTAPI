from fastapi import FastAPI
from .routers import auth
from .database import engine
from . import models

# Create tables on startup (for development; use Alembic in production)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI JWT Auth with Argon2")


app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "FastAPI JWT Auth API is running!"}