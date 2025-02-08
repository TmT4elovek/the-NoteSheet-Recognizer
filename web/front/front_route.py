from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

front = APIRouter()

front.mount("/static", StaticFiles(directory=r"web\backend\static"), name="static")
templates = Jinja2Templates(r'web\backend\static\templates')


@front.get('/')
async def main(request: Request):
    return templates.TemplateResponse(request, 'index.html', {'request': request, 'title': 'Bebra'})