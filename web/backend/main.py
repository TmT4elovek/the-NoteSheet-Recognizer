import os

from fastapi import FastAPI, UploadFile, Body, HTTPException
from fastapi.responses import Response

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from static.Entity import MusicSheet, User, RecognizedMusicSheet, SQLALCHEMY_DATABASE_URL


UPLOAD_FOLDER = "\\the-NoteSheet-Recognizer\\web\\backend\\static\\files\\music_sheets"


app = FastAPI()
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# @app.get("/api/")
# async def root():
#     return Response('Hello, world!')

@app.post('/api/add-music-sheet/')
async def add_file(file: UploadFile):
    with Session(engine) as db:
        # insert new file into the database
        music = MusicSheet(user_id=0, music_sheet=file.filename, title='MUsic')
        db.add(music)
        db.commit()

    try:
        # Сохраняем файл на диск
        file_path = os.path.join(__file__.split('\\')[:-4], UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.file.read())
    except Exception as e:
        print(f"Error saving file: {e}")
        raise HTTPException(500, 'Error saving file')
    #TODO Дописать код для сохранения полученного файла


@app.post('/api/add-user/')
async def add_user(name: str = Body(embed=True, max_length=30),
                    password: str = Body(embed=True, max_length=40)
                    ):
    with Session(engine) as db:
        # insert new user into the database
        user = User(name=name, password=password)
        db.add(user)
        db.commit()

@app.get('/api/get-user/{user_id}')
async def get_user(user_id):
    with Session(engine) as db:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)