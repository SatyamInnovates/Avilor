from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from supabase import create_client
import os

templates = Jinja2Templates(directory='template')

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

router = APIRouter()

@router.get("/login")
def login_page(request: Request, next: str = None,signup: str = None):
    is_logged_in = request.cookies.get("access_token") is not None
    return templates.TemplateResponse(request, 'login.html', {"is_logged_in": is_logged_in, "next": next})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), next: str = Form(None)):
    try:
        print(f"Attempting login with {email}")
        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print(f"Login success: {session}")
        if next == "workspace" and request.session.get("onboarding"):
            redirect_url = "/onboarding/continue"
        else:
            redirect_url = "/"
        response = RedirectResponse(url=redirect_url, status_code=303)
        response.set_cookie("access_token", session.session.access_token)
        return response
    except Exception as e:
        print(f"Login error: {e}")
        return templates.TemplateResponse(request, 'login.html', {"error": "Invalid credentials", "next": next})

@router.get("/signup")
def signup_page(request: Request):
    is_logged_in = request.cookies.get("access_token") is not None
    return templates.TemplateResponse(request, 'signup.html', {"is_logged_in": is_logged_in})


@router.post("/signup")
def signup(request: Request, email: str = Form(...), username: str = Form(...), password: str = Form(...)):
    try:
        result = supabase.auth.sign_up({"email": email, "password": password})
        user_id = result.user.id
        
        supabase.table('users').insert({
            "id": user_id,
            "email": email,
            "username": username
        }).execute()
        
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        print(f"Signup error: {e}")
        return templates.TemplateResponse(request, 'signup.html', {"error": "Account already exists. Try logging in."})
    
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/auth/callback")
def auth_callback(request: Request):
    return RedirectResponse(url="/login?signup=success", status_code=303)


@router.get("/signup")
async def auth_google():
    response = supabase.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {
                "redirect_to": "https://avilor.onrender.com/auth/callback"
            }
        }
    )

    return RedirectResponse(response.url)