from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
load_dotenv()
from routers import home, auth , profile , onboarding , workspace , pricing ,about,todays
from starlette.middleware.sessions import SessionMiddleware



app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-dev-secret-key-12345")


app.include_router(home.router)

app.include_router(auth.router)

app.include_router(profile.router)

app.include_router(onboarding.router)

app.include_router(workspace.router)

app.include_router(pricing.router)

app.include_router(about.router)

app.include_router(todays.router)