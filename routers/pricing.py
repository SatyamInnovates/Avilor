from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='template')

router = APIRouter()



@router.get("/pricing")
def show_pricing(request: Request):
    is_logged_in = request.cookies.get("access_token") is not None
    return templates.TemplateResponse(request, "pricing.html", {"is_logged_in": is_logged_in})

