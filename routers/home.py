from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory='template')
router = APIRouter()

def get_is_logged_in(request: Request):
    return request.cookies.get("access_token") is not None

@router.get("/")
def home(request: Request):
    is_logged_in = get_is_logged_in(request)
    return templates.TemplateResponse(request, 'home.html', {"is_logged_in": is_logged_in})

