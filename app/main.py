from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import models
from app.routers import licenses, users, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="License API", description="API for managing software licenses")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในการใช้งานจริงควรระบุ domain ที่อนุญาตเท่านั้น
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router, tags=["Users"])
app.include_router(licenses.router, tags=["Licenses"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to License API"}