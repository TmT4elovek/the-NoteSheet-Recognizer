import os

from fastapi import FastAPI, UploadFile, Body, HTTPException
from fastapi.responses import Response

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from static.Entity import MusicSheet, User, RecognizedMusicSheet, SQLALCHEMY_DATABASE_URL


app = FastAPI()
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

@app.get('/api/get-user/{user_id}')
async def get_user(user_id: int):
    with Session(engine) as db:
        user = db.query(User).filter(User.id == user_id).first()
        return user

@app.get('/api/get-recognized-music-sheet/{music_sheet_id}')
async def get_recognized_music_sheet(music_sheet_id: int):
    with Session(engine) as db:
        music_sheet = db.query(MusicSheet).filter(MusicSheet.id == music_sheet_id).first()
        recognized_music_sheet = db.query(RecognizedMusicSheet).filter(RecognizedMusicSheet.sheet_id == music_sheet_id).first()
        return {
            "music_sheet": music_sheet.to_dict(),
            "recognized_music_sheet": recognized_music_sheet.to_dict() if recognized_music_sheet else None
        }

@app.post('/api/create-recognized-music-sheet/{music_sheet_id}')
async def create_recognized_music_sheet(music_sheet_id: int):
    #TODO привязать данный эндпоинт к нейронке и добавлять её ответ в базу данных
    pass

@app.post('/api/add-music-sheet/')
async def add_file(file: UploadFile):
    with Session(engine) as db:
        # insert new file into the database
        music = MusicSheet(user_id=0, music_sheet=file.filename, title='MUsic')
        db.add(music)
        db.commit()
    try:
        # Сохраняем файл на диск
        file_path = os.path.join('web', 'backend', 'static', 'files', 'music_sheets', file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        print(f"Error saving file: {e}")
        raise HTTPException(500, 'Error saving file')

@app.post('/api/add-user/')
async def add_user(name: str = Body(embed=True, max_length=30),
                    password: str = Body(embed=True, max_length=40)
                    ):
    with Session(engine) as db:
        # insert new user into the database
        user = User(name=name, password=password)
        db.add(user)
        db.commit()

@app.delete('/api/delete-user/{id}')
async def delete_user(id: int):
    with Session(engine) as db:
        user = db.query(User).filter(User.id == id).first()
        if user:
            db.delete(user)
            db.commit()
        else:
            raise HTTPException(404, 'User not found')

@app.delete('/api/delete-music-sheet/{id}')
async def delete_music_sheet(id: int):
    with Session(engine) as db:
        music_sheet = db.query(MusicSheet).filter(MusicSheet.id == id).first()
        if music_sheet:
            db.delete(music_sheet)
            db.commit()
        else:
            raise HTTPException(404, 'Music sheet not found')

@app.delete('/api/delete-recognized-music-sheet/{id}')
async def delete_recognized_music_sheet(id: int):
    with Session(engine) as db:
        recognized_music_sheet = db.query(RecognizedMusicSheet).filter(RecognizedMusicSheet.id == id).first()
        if recognized_music_sheet:
            db.delete(recognized_music_sheet)
            db.commit()
        else:
            raise HTTPException(404, 'Recognized music sheet not found')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)

    ##! Swagger
    ##! http://(adress)/docs