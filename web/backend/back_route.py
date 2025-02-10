import os

from fastapi import FastAPI, UploadFile, Body, HTTPException, Request, APIRouter
from fastapi.responses import Response, RedirectResponse
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import torchvision.transforms as tr
from PIL import Image


from backend.static.Entity import MusicSheet, User, RecognizedMusicSheet, SQLALCHEMY_DATABASE_URL
from backend.music21_release import recognize
from backend.neural_network_utils import utils
from backend.neural_network_utils import parametrs


back = APIRouter(prefix='/api', tags=['Backend'])

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
yolov3_m, yolov3_l = utils.import_models()


@back.get('/api/get-user/{user_id}')
async def get_user(user_id: int):
    with Session(engine) as db:
        user = db.query(User).filter(User.id == user_id).first()
        return user

@back.post('/api/check-user')
async def check_user(request: Request, username: str = Body(embed=True), password: str = Body(embed=True)):
    with Session(engine) as db:
        user = db.query(User).filter(User.username == username).first()
        if user and user.password == password:
            return Response(user.to_dict(), status=202)
        return Response(status_code=404)

@back.get('/api/get-recognized-music-sheet/{music_sheet_id}')
async def get_recognized_music_sheet(music_sheet_id: int):
    with Session(engine) as db:
        music_sheet = db.query(MusicSheet).filter(MusicSheet.id == music_sheet_id).first()
        recognized_music_sheet = db.query(RecognizedMusicSheet).filter(RecognizedMusicSheet.sheet_id == music_sheet_id).first()
        return {
            "music_sheet": music_sheet.to_dict(),
            "recognized_music_sheet": recognized_music_sheet.to_dict() if recognized_music_sheet else None
        }


@back.post('/api/create-recognized-music-sheet/{music_sheet_id}')
async def create_recognized_music_sheet(music_sheet_id: str):
    music_sheets = list()
    with Session(engine) as db:
        for id in music_sheet_id.split(";"):
            music_sheets.append(db.query(MusicSheet).filter(MusicSheet.id == int(id)).first())
    images = list()
    for j in music_sheets:
        file_name = j.music_sheet
        if any(file_name.endswith(file_type) for file_type in parametrs.FORMATS):
            img = Image.open(f"static\\files\\music_sheets\\{j.music_sheet}")
            images.append(img)
    if len(images) == 0:
        # TODO: Оповещение
        return 1
    mp3 = recognize(images)
    with Session(engine) as db:
        # insert new file into the database
        for i in music_sheets:
            sheet = RecognizedMusicSheet(recognized_music=await mp3.read(), sheet_id=music_sheet_id)
            i.recognized_music_sheet = sheet
            db.commit()
    return 0



@back.post('/api/add-music-sheet/')
async def add_file(request: Request, files: list[UploadFile]):
    user_id = request.cookies.get('id')
    try:
        # Читаем содержимое файла
        

        with Session(engine) as db:
            # Изменяем статус у старых листов
            last_sheets = db.query(MusicSheet).filter(MusicSheet.last == True).all()
            for sheet in last_sheets:
                sheet.last = False
            # Сохраняем файл в базе данных
            for file in files:
                content = await file.read()
                music = MusicSheet(user_id=user_id, music_sheet=content, title=file.filename, last=True)
                user = db.query(User).filter(User.id == user_id).first()
                user.music_sheets.append(music)
                db.commit()

    except Exception as e:
        print(f"Error saving file to database: {e}")
        raise HTTPException(500, 'Error saving file to database')


@back.post('/api/add-user/')
async def add_user(request: Request, username: str = Body(embed=True, max_length=30), password: str = Body(embed=True, max_length=40)):
    with Session(engine) as db:
        # insert new user into the database
        user = User(name=username, password=password)
        db.add(user)
        db.commit()

@back.delete('/api/delete-user/{id}')
async def delete_user(id: int):
    with Session(engine) as db:
        user = db.query(User).filter(User.id == id).first()
        if user:
            db.delete(user)
            db.commit()
        else:
            raise HTTPException(404, 'User not found')


@back.delete('/api/delete-music-sheet/{id}')
async def delete_music_sheet(id: int):
    with Session(engine) as db:
        music_sheet = db.query(MusicSheet).filter(MusicSheet.id == id).first()
        if music_sheet:
            db.delete(music_sheet)
            db.commit()
        else:
            raise HTTPException(404, 'Music sheet not found')


@back.delete('/api/delete-recognized-music-sheet/{id}')
async def delete_recognized_music_sheet(id: int):
    with Session(engine) as db:
        recognized_music_sheet = db.query(RecognizedMusicSheet).filter(RecognizedMusicSheet.id == id).first()
        if recognized_music_sheet:
            db.delete(recognized_music_sheet)
            db.commit()
        else:
            raise HTTPException(404, 'Recognized music sheet not found')