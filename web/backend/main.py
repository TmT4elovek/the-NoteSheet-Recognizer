from fastapi import FastAPI, UploadFile
from fastapi.responses import Response

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from static.Entity import MusicSheet, SQLALCHEMY_DATABASE_URL


app = FastAPI()
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

@app.get("/")
async def root():
    return Response('Hello, world!')

@app.post('/add-file/')
async def add_file(file: UploadFile):
    with Session(engine) as db:
        # insert new file into the database
        music = MusicSheet(user_id=0, music_sheet=file.filename, title='MUsic')
        db.add(music)
        db.commit()