from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers.auth import supabase

templates = Jinja2Templates(directory='template')
router = APIRouter()


@router.get("/profile")
def profile_show(request: Request):
    token = request.cookies.get("access_token")
    is_logged_in = token is not None
    
    user_email = None
    username = None
    if is_logged_in:
        user = supabase.auth.get_user(token)
        user_email = user.user.email
        user_data = supabase.table("users").select('username').eq('email',user_email).execute()
        if user_data.data:
            username = user_data.data[0]['username']
    return templates.TemplateResponse(request, 'profile.html', {
        "is_logged_in": is_logged_in,
        "user_email": user_email,
        "username" : username
    })
    
    