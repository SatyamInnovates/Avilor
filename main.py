from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os
load_dotenv()
from routers import home, auth, profile, onboarding, workspace, pricing, about, todays
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))


supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def today_ist():
    return datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()


@app.middleware("http")
async def track_visit(request: Request, call_next):
    path = request.url.path
    if not path.startswith(("/static", "/favicon")):
        token = request.cookies.get("access_token")
        if token:
            try:
                user = supabase.auth.get_user(token)
                user_id = user.user.id
                supabase.table("daily_visits").upsert(
                    {"user_id": user_id, "visit_date": today_ist()},
                    on_conflict="user_id,visit_date",
                    ignore_duplicates=True
                ).execute()
            except Exception as e:
                print(f"daily_visit error: {e}")

    response = await call_next(request)
    return response


app.include_router(home.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(onboarding.router)
app.include_router(workspace.router)
app.include_router(pricing.router)
app.include_router(about.router)
app.include_router(todays.router)