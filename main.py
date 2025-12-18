from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import auth

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL working!"}

# Async DB initialization on startup
@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        # Run sync create_all inside async engine
        await conn.run_sync(models.Base.metadata.create_all)
