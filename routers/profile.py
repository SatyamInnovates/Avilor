from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers.auth import supabase

templates = Jinja2Templates(directory='template')
router = APIRouter()


@router.get("/profile")
def profile_show(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        user = supabase.auth.get_user(token)
        user_email = user.user.email
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

    user_data = supabase.table("users").select('username').eq('email', user_email).execute()
    username = user_data.data[0]['username'] if user_data.data else None

    return templates.TemplateResponse(request, 'profile.html', {
        "is_logged_in": True,
        "user_email": user_email,
        "username": username
    })
    
    