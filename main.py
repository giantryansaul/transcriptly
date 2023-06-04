from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import SessionLocal, engine

app = FastAPI()

# add middleware to enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create the database tables
models.Base.metadata.create_all(bind=engine)


# dependency to get a database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/characters", response_model=schemas.Character)
def create_character(character: schemas.CharacterCreate, db: Session = Depends(get_db)):
    db_character = models.Character(name=character.name, race=character.race, class_=character.class_)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@app.get("/characters", response_model=List[schemas.Character])
def read_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    characters = db.query(models.Character).offset(skip).limit(limit).all()
    return characters
