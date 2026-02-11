from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine
from app import models
from app.routers import auth
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)

app = FastAPI()

# Register global handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routes
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
