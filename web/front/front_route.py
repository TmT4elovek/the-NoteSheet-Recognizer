from fastapi import APIRouter, File, Request, Form, Body, Cookie, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse, Response
# from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from authx import AuthXConfig, AuthX
from datetime import timedelta

front = APIRouter(tags=['Frontend'])


templates = Jinja2Templates(r'web\front\static\templates')

config = AuthXConfig()
config.JWT_SECRET_KEY = 'secret'
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
# config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=120)

authx = AuthX(config)


@front.get('/register')
async def register(request: Request):
    return templates.TemplateResponse(request, 'register.html', {'request': request})


@front.get('/login')
async def login(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'request': request})

@front.get('/')
async def home(request: Request):
    return templates.TemplateResponse(request, 'home.html', {'request': request, 'is_user': True})

@front.get('/account')
async def account(request: Request):
    return templates.TemplateResponse(request, 'account.html', {'request': request})

@front.get('/token')
async def token(my_access_token = Cookie(), user_data = Cookie()):
    return 'window.location.href = "/login"'
#!BACK
@front.post('/api/check-user')
async def check_user(request: Request, response: Response, username: str = Body(embed=True, min_length=5), password: str = Body(embed=True, min_length=8)):
        user = {'username': username, 'password': password}

        if user and user['password'] == password:
            access_token = authx.create_access_token(uid='0')

            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
            response.set_cookie('user_data', user)
            return {'access_token': access_token}
        return Response(status_code=404)


@front.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_img = await file.read()
    return {"filename": file.filename, "content_type": file.content_type}