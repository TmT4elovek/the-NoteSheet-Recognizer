from fastapi import APIRouter, Request, Form, Body
from fastapi.responses import RedirectResponse
# from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

front = APIRouter(prefix='/front', tags=['Frontend'])


templates = Jinja2Templates(r'web\front\static\templates')


@front.get('/')
async def main(request: Request):
    return templates.TemplateResponse(request, 'register.html', {'request': request, 'title': 'Register'})

@front.post('/api/add-user')
async def register(request: Request, username: str = Body(embed=True, max_length=30), password: str = Body(embed=True, max_length=40)):
    redirect_url = request.url_for('login')
    return RedirectResponse('/login', 303)

@front.get('/login', name='login')
async def login(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'request': request, 'title': 'Login'}, headers={'Location': 'http://127.0.0.1:8000/login'})