from app.database.connection import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.models import Project

app = FastAPI(title="ShipForge API")

Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ShipForge API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
