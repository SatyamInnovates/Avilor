from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from routers.auth import supabase
import json
from fastapi.responses import RedirectResponse, JSONResponse
from repository.workspace import generate_questions, validate_answers

router = APIRouter()
templates = Jinja2Templates(directory='template')


@router.get("/workspace/whats-new")
def whats_new(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        supabase.auth.get_user(token)
    except Exception:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, 'whats_new.html', {"is_logged_in": True})


@router.get("/workspace")
def show_workspace(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

    final_roadmap = None
    user_role = None  # default so it's always defined even if no roadmap yet

    result = supabase.table('roadmaps').select('roadmap_content, role').eq('user_id', user_id).order('created_at', desc=True).execute()
    if result.data:
        try:
            pre_roadmap = result.data[0]['roadmap_content'].strip().replace("```json", "").replace("```", "").strip()
            final_roadmap = json.loads(pre_roadmap)
            user_role = result.data[0].get('role', 'Developer')
        except Exception as e:
            print(f"JSON parse failed - {e}")

    try:
        prog = supabase.table("progress").select("completed_phases").eq('user_id', user_id).execute()
        completed_phases = sorted(prog.data[0].get('completed_phases') or []) if prog.data else []
    except Exception:
        completed_phases = []

    return templates.TemplateResponse(request, 'workspace.html', {
        "roadmap": final_roadmap,
        "role": user_role,
        "is_logged_in": True,
        "user_id": user_id,
        "completed_phases": completed_phases
    })


def _default_questions():
    return [
        "What was the main concept covered in this phase?",
        "Describe one practical thing you can now do that you couldn't do before."
    ]


@router.get("/workspace/micro-check/{phase_index}")
async def get_micro_questions(request: Request, phase_index: int):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse({"questions": _default_questions()})
    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return JSONResponse({"questions": _default_questions()})

    result = supabase.table('roadmaps').select('roadmap_content').eq('user_id', user_id).order('created_at', desc=True).execute()
    if not result.data:
        return JSONResponse({"questions": _default_questions()})

    try:
        content = result.data[0]['roadmap_content'].strip().replace("```json", "").replace("```", "").strip()
        roadmap = json.loads(content)
        phase = roadmap[phase_index]
        topic = phase.get('resource_query') or phase.get('phase', 'programming')
        questions = generate_questions(phase.get('phase', ''), topic)
        return JSONResponse({"questions": questions})
    except Exception as e:
        print(f"micro-check generate error: {e}")
        return JSONResponse({"questions": _default_questions()})



@router.post("/workspace/micro-check/submit")
async def submit_micro_check(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse({"error": "not logged in"}, status_code=401)
    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return JSONResponse({"error": "invalid token"}, status_code=401)

    body = await request.json()
    phase_index = int(body.get('phase_index', 0))
    questions = body.get('questions', [])
    answers = body.get('answers', [])

    phase_name = ''
    topic = ''
    try:
        result = supabase.table('roadmaps').select('roadmap_content').eq('user_id', user_id).order('created_at', desc=True).execute()
        if result.data:
            content = result.data[0]['roadmap_content'].strip().replace("```json", "").replace("```", "").strip()
            roadmap = json.loads(content)
            phase = roadmap[phase_index]
            phase_name = phase.get('phase', '')
            topic = phase.get('resource_query') or phase_name
    except Exception as e:
        print(f"submit_micro_check: could not load phase context: {e}")
    if not questions or not answers:
        return JSONResponse({"error": "missing answers"}, status_code=400)
    if questions and answers:
        passed = validate_answers(phase_name, topic, questions, answers)
        if not passed:
            return JSONResponse({"success": False, "redirect": f"/workspace/tutor?phase={phase_index}"})

    try:
        prog = supabase.table("progress").select("completed_phases").eq('user_id', user_id).execute()
        existing = list(prog.data[0].get('completed_phases') or []) if prog.data else []
        if phase_index not in existing:
            existing.append(phase_index)
        supabase.table("progress").update({"completed_phases": existing}).eq('user_id', user_id).execute()
    except Exception as e:
        print(f"submit_micro_check DB error: {e}")
        return JSONResponse({"error": "DB error"}, status_code=500)

    return JSONResponse({"success": True})



