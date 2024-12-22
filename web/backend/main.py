from fastapi import FastAPI, UploadFile
from fastapi.responses import Response

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from static.config import SQLALCHEMY_DATABASE_URL
from static.Entity import MusicSheet


app = FastAPI()
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

@app.get("/")
async def root():
    return Response('Hello, world!')

@app.post('/add-file')
async def add_file(file: UploadFile):
    return {"filename": file.filename}
    # with Session(engine) as db:
    #     # insert new file into the database
    #     music = MusicSheet(user_id=0, music_sheet=file.name, title='MUsic')
    #     db.add(music)
    #     db.commit()
    #TODO понять, почему выскакивает ошибка 422