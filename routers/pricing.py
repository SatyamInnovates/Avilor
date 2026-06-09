from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='template')

router = APIRouter()



@router.get("/pricing")
def show_pricing(request:Request):
    pricing = "not set yet it is free"
    return templates.TemplateResponse(request,"pricing.html",{"pricing":pricing})

