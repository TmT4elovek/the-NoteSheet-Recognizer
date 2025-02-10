from typing import List
from fastapi import APIRouter, File, Request, Form, Body, Cookie, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse, Response
# from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from authx import AuthXConfig, AuthX
from datetime import timedelta

front = APIRouter(tags=['Frontend'])


templates = Jinja2Templates(r'web\backend\front\static\templates')

config = AuthXConfig()
config.JWT_SECRET_KEY = 'secret'
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

authx = AuthX(config)


@front.get('/register')
async def register(request: Request):
    return templates.TemplateResponse(request, 'register.html', {'request': request})

@front.get('/login')
async def login(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'request': request})

@front.get('/')
async def home(request: Request):
    my_access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if my_access_token:
        is_user = True
    else:
        is_user = False
    return templates.TemplateResponse(request, 'home.html', {'request': request, 'is_user': is_user})

@front.get('/account')
async def account(request: Request, username = Cookie(...)):
    return templates.TemplateResponse(request, 'account.html', {'request': request, 'user': username})


#!BACK
@front.post('/api/check-user')
async def check_user(request: Request, response: Response, username: str = Body(embed=True, min_length=5), password: str = Body(embed=True, min_length=8)):
        class User:
            def __init__(self, username, password):
                self.username = username
                self.password = password
                self.id = 0

        user = User(username, password)        

        if user and user.password == password:
            access_token = authx.create_access_token(uid=str(user.id))

            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
            response.set_cookie('username', user.username)
            response.set_cookie('id', user.id)
            return {'access_token': access_token}
        return Response(status_code=404)


@front.post("/api/add-music-sheet")
async def upload_file(request: Request, files: list[UploadFile]):
    res = list()
    for file in files:
        file_img = await file.read()
        res.append(file.filename)
    return res