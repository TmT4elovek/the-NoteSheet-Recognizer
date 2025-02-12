from typing import List
from fastapi import APIRouter, File, Request, Form, Body, Cookie, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse, Response
# from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from authx import AuthXConfig, AuthX
from datetime import timedelta

front = APIRouter(tags=['Frontend'])


templates = Jinja2Templates(r'/home/keglya300/the-NoteSheet-Recognizer/web/backend/front/static/templates')

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
    return templates.TemplateResponse(request, 'home.html', {'request': request, 'is_user': is_user, })

@front.get('/account')
async def account(request: Request, username = Cookie(...)):
    return templates.TemplateResponse(request, 'account.html', {'request': request, 'user': username})
