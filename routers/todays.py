from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from routers.auth import supabase
import json

templates = Jinja2Templates(directory='template')
router = APIRouter()


@router.get("/workspace/today-focus")
def show_todaysfocus(request: Request):
    token = request.cookies.get("access_token")
    user = supabase.auth.get_user(token)
    user_id = user.user.id
    result = supabase.table('roadmaps').select('roadmap_content').eq('user_id', user_id).order('created_at', desc=True).execute()

    final_roadmap = None
    if result.data:
        fetched_answer = result.data[0]['roadmap_content']
        try:
            pre_roadmap = fetched_answer.strip().replace("```json", "").replace("```", "").strip()
            final_roadmap = json.loads(pre_roadmap)
        except Exception as e:
            print(f"JSON parse failed - {e}")
            final_roadmap = None


    prog = supabase.table("progress").select("*").eq('user_id', user_id).execute()
    if prog.data:
        current_phase = prog.data[0]['current_phase']
        current_step = prog.data[0]['current_step']
    else:
        current_phase = 0
        current_step = 0
        supabase.table('progress').insert({
            "user_id": user_id,
            "current_phase": 0,
            "current_step": 0
        }).execute()

    todays_data = None
    if final_roadmap:
        try:
            current_phase = min(current_phase, len(final_roadmap) - 1)
            current_step = min(current_step, len(final_roadmap[current_phase]["steps"]) - 1)
            phase = final_roadmap[current_phase]
            step = phase["steps"][current_step]

            todays_data = {
                "phase_name": phase["phase"],
                "phase_number": current_phase + 1,
                "total_phases": len(final_roadmap),
                "step_title": step["title"],
                "step_number": current_step + 1,
                "total_steps": len(phase["steps"]),
                "resource_query": step["resource_query"],
                "tasks": step["tasks"],
                "duration": phase.get("duration", ""),
                "avoid": phase.get("avoid", [])
            }
        except Exception as e:
            print(f"Extraction failed - {e}")
            todays_data = None

    is_logged_in = request.cookies.get("access_token") is not None
    return templates.TemplateResponse(request, 'today_focus.html', {
        "todays_data": todays_data,
        "is_logged_in": is_logged_in
    })


@router.post("/workspace/today-focus")
def next_step(request: Request):
    token = request.cookies.get("access_token")
    user = supabase.auth.get_user(token)
    user_id = user.user.id

    result = supabase.table('roadmaps').select('roadmap_content').eq('user_id', user_id).order('created_at', desc=True).execute()
    roadmap = json.loads(result.data[0]['roadmap_content'].strip().replace("```json", "").replace("```", "").strip())

    prog = supabase.table('progress').select('*').eq('user_id', user_id).execute()
    current_phase = prog.data[0]['current_phase']
    current_step = prog.data[0]['current_step']

    current_step += 1
    if current_step >= len(roadmap[current_phase]["steps"]):
        current_step = 0
        current_phase += 1
        if current_phase >= len(roadmap):
            current_phase = len(roadmap) - 1
            current_step = len(roadmap[current_phase]["steps"]) - 1

    supabase.table('progress').update({
        "current_phase": current_phase,
        "current_step": current_step
    }).eq('user_id', user_id).execute()

    return RedirectResponse(url='/workspace/today-focus', status_code=303)