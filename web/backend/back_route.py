import os

from fastapi import FastAPI, Form, UploadFile, Body, HTTPException, Request, APIRouter
from fastapi.responses import Response, RedirectResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

import torchvision.transforms as tr
from PIL import Image

from io import BytesIO


from backend.static.Entity import MusicSheet, User, RecognizedMusicSheet, SQLALCHEMY_DATABASE_URL
from backend.neural_network_utils import parametrs
from backend.neural_network_utils import utils
from backend.music21_release import recognize
#! НА РЕЛИЗЕ
from backend.front.front_route import authx, config, templates


back = APIRouter(tags=['Backend'])

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
yolov3_m, yolov3_l = utils.import_models()


@back.get('/api/get-user/{user_id}')
async def get_user(user_id: int):
    with Session(engine) as db:
        user = db.query(User).filter(User.id == user_id).first()
        return user

@back.post('/api/check-user') #! Login
async def check_user(request: Request, response: Response, username: str = Body(embed=True), password: str = Body(embed=True)):
    with Session(engine) as db:
        try:
            user = db.query(User).filter(User.username == username).first()
        except OperationalError:
            raise HTTPException(status_code=404, detail="Database error")
        if user and user.password == password:
            access_token = authx.create_access_token(uid=str(user.id))
            print("Access Log In")
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
            response.set_cookie('username', user.username)
            response.set_cookie('id', user.id)
            response.status_code = 200
            # return {'access_token': access_token}
            return response
        raise HTTPException(status_code=404, detail="Database error")

@back.get('/api/get-recognized-music-sheet/')
async def get_recognized_music_sheet(request: Request):

    with Session(engine) as db:
        recognized_music_sheet = db.query(RecognizedMusicSheet).filter(RecognizedMusicSheet.id == request.cookies.get("rec_sheet_id")).first()
    byte_stream = BytesIO(recognized_music_sheet.recognized_music)
    headers = {
        f"Content-Disposition": "attachment; filename=audio.mp3"  # Замените на желаемое имя файла и расширение
    }
    response = StreamingResponse(byte_stream, media_type='audio/mpeg', headers=headers)
    return response


@back.get("/api/get-history")
async def history(request: Request, response: Response):
    id = request.cookies.get("id")
    result = list()

    with Session(engine) as db:
        auds = db.query(RecognizedMusicSheet
                        ).filter(RecognizedMusicSheet.user_id == id
                        ).order_by(desc(RecognizedMusicSheet.created_at)).limit(5).all()
        for aud in auds:
            result.append(aud.recognized_music)


@back.post('/api/create-recognized-music-sheet/')
async def create_recognized_music_sheet(request: Request, response: Response):
    music_sheet_id = request.cookies.get('sheets_ids')
    music_sheets = list()
    with Session(engine) as db:
        for id in music_sheet_id.split(";"):
            music_sheets.append(db.query(MusicSheet).filter(MusicSheet.id == int(id)).first())
    images = list()
    for j in music_sheets:
        img = Image.open(f"static\\files\\music_sheets\\{j.music_sheet}")
        images.append(img)
        file_name = j.music_sheet
        if any(file_name.endswith(file_type) for file_type  in parametrs.FORMATS):
            img = Image.open(f"static\\files\\music_sheets\\{j.music_sheet}")
            images.append(img)
    if len(images) == 0:
        # TODO: Оповещение
        return
    mp3 = recognize(images, yolov3_m, yolov3_l)
    mp3_byte = await mp3.read()
    with Session(engine) as db:
        # insert new file into the database
        sheet = RecognizedMusicSheet(recognized_music=mp3_byte, user_id=request.cookies.get('id'))
        sheet_id = sheet.id
        db.add(sheet)
        for i in music_sheets:
            i.recognized_music_sheet = sheet
        db.commit()
    
    response = templates.TemplateResponse("home.html", {"request": request, "user": True, "audio": mp3.filename})
    response.set_cookie('rec_sheet_id', sheet_id)
    return response



@back.post('/api/add-music-sheet/')
async def add_file(request: Request, response: Response, files: list[UploadFile]):
    user_id = request.cookies.get('id')
    print(user_id)
    try:
        sheets_ids = list()
        with Session(engine) as db:
            # Изменяем статус у старых листов
            last_sheets = db.query(MusicSheet).filter(MusicSheet.last == True).all()
            for sheet in last_sheets:
                sheet.last = False
            # Сохраняем файл в базе данных
            for file in files:
                print(file.filename)
                content = await file.read()
                music = MusicSheet(user_id=user_id, music_sheet=content, title=file.filename, last=True)
                user = db.query(User).filter(User.id == user_id).first()
                user.music_sheet.append(music)
                sheets_ids.append(str(music.id))
                db.add(music)
            db.commit()
        response = templates.TemplateResponse("home.html", {"request": request, "user": True})
        return response.set_cookie('sheets_ids', ';'.join(sheets_ids))
    except Exception as e:
        print(f"Error saving file to database: {e}")
        raise HTTPException(500, 'Error saving file to database')


@back.post('/api/add-user/')
async def add_user(request: Request, username: str = Body(embed=True, max_length=30), password: str = Body(embed=True, max_length=40)):
    with Session(engine) as db:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            # insert new user into the database
            user = User(name=username, password=password)
            db.add(user)
            db.commit()
        else:
            raise HTTPException(409, 'User with this username already exists')


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