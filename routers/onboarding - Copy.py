from fastapi import FastAPI, Request, APIRouter, Form
from repository.onboarding import get_questions
from schemas.onboarding import OnboardingAnswers
from repository.workspace import ai, intent_to_focus
from routers.auth import supabase
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json

templates = Jinja2Templates(directory='template')
router = APIRouter()
goal_to_role = {
        "Websites & Web Apps": "Web Developer",
        "Phone Apps": "Mobile App Developer",
        "AI & Smart Systems": "AI/ML Engineer",
        "Data Analysis": "Data Analyst",
        "Games": "Game Developer",
        "Server & Infrastructure": "Backend / DevOps Engineer"
        } 

@router.get("/onboarding")
def show_questions(request: Request):
    questions = get_questions()
      
    is_logged_in = request.cookies.get("access_token") is not None
    return templates.TemplateResponse(request, 'onboarding.html', {"questions": questions, "is_logged_in": is_logged_in})


@router.post("/onboarding")
def submit_onboarding(request: Request, q1: str = Form(...), q2: str = Form(...), q3: str = Form(...), q4: str = Form(...), q5: str = Form(...) ):
    answers = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5}
    
    request.session["onboarding"] = answers

    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url='/login?next=workspace', status_code=303)

    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return RedirectResponse(url='/login?next=workspace', status_code=303)

    try:
        checked_answers = OnboardingAnswers(**answers)
    except Exception as e:
        print(f"VALIDATION FAILED - {e}")
        return RedirectResponse(url='/onboarding', status_code=303)

    try:
        focus = intent_to_focus.get(checked_answers.q1, "Build solid, practical coding skills toward their goal.")
        ai_roadmap = ai(checked_answers,focus)
    except Exception as e:
        print(f"AI generation failed - {e}")
        return templates.TemplateResponse(request, 'onboarding.html', {
            "questions": get_questions(),
            "is_logged_in": True,
            "error": "AI is temporarily unavailable. Please try again in a moment."
        })

    role = goal_to_role.get(checked_answers.q2)
    supabase.table('roadmaps').insert({
        "user_id": user_id,
        "roadmap_content": ai_roadmap,
        "role": role
    }).execute()

    request.session.pop("onboarding", None)
    return RedirectResponse(url='/workspace', status_code=303)


@router.get("/onboarding/continue")
def continue_onboarding(request: Request):
    
    answers = request.session.get("onboarding")
    if not answers:
        return RedirectResponse(url='/onboarding', status_code=303)

    token = request.cookies.get("access_token")
    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return RedirectResponse(url='/login?next=workspace', status_code=303)

    try:
        
        checked_answers = OnboardingAnswers(**answers)
    except Exception as e:
        print(f"VALIDATION FAILED - {e}")
        return RedirectResponse(url='/onboarding', status_code=303)
    focus = intent_to_focus.get(checked_answers.q1, "Build solid, practical coding skills toward their goal.")
    ai_roadmap = ai(checked_answers,focus)
    role = goal_to_role.get(checked_answers.q2)
    supabase.table('roadmaps').insert({
        "user_id": user_id,
        "roadmap_content": ai_roadmap,
        "role" : role
    }).execute()
    


    request.session.pop("onboarding", None)
    return RedirectResponse(url='/workspace', status_code=303)



