from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='template')

router = APIRouter()



@router.get("/about")
def show_pricing(request:Request):
    about = "asd"
    return templates.TemplateResponse(request,"about.html",{"about":about})
