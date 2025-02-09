from fastapi import APIRouter, Request, Form, Body, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

front = APIRouter(tags=['Frontend'])


templates = Jinja2Templates(r'web\front\static\templates')


@front.get('/register')
async def main(request: Request):
    return templates.TemplateResponse(request, 'register.html', {'request': request, 'title': 'Register'})

@front.post('/api/check-user')
async def check_user(request: Request, username: str = Body(embed=True, min_length=5), password: str = Body(embed=True, min_length=8)):
        user = {'username': username, 'password': password}

        if user and user['password'] == password:
            return JSONResponse(jsonable_encoder(user), status_code=202)
        return Response(status_code=404)

@front.get('/login')
async def login(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'request': request, 'title': 'Login'})