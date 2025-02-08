from fastapi import APIRouter, Request, Form
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

front = APIRouter(tags=['Frontend'])

front.mount("/static", StaticFiles(directory=r"web\front\static"), name="static")
templates = Jinja2Templates(r'web\front\static\templates')


@front.get('/')
async def main(request: Request):
    return templates.TemplateResponse(request, 'index.html', {'request': request, 'title': 'Bebra'})

@front.post('/api/add-user')
async def register(form):
    return {"username": form['username'], "password": form['password']}