from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from routers.auth import supabase
import json

templates = Jinja2Templates(directory="template")

router = APIRouter()

@router.get("/workspace/todays-focus")
def show_todaysfocus(request:Request):
    token = request.cookies.get("access_token")
    user = supabase.auth.get_user(token)
    user_id = user.user.id
    roadmap = supabase.table("roadmaps").select('roadmap_content').eq("user_id",user_id).execute()
    if roadmap.data:
        result = roadmap.data[0]['roadmap_content']
        clean = result.strip().replace("```json", "").replace("```", "").strip()
        final_roadmap = json.loads(clean)
    prog = supabase.table("progress").select("*").eq("user_id",user_id).execute()
        
    if prog.data:
        current_phase = prog.data[0]['current_phase']
        current_step = prog.data[0]['current_step']
    else:
        current_phase = 0 
        current_step = 0
         
        supabase.table('progress').insert({
            "user_id" : user_id,
            "current_phase" : 0,
            "current_step" : 0
        }).execute()
        
    phase = final_roadmap[current_phase]
    step = phase["steps"][current_step]

    todays_data = {
        "phase_name": phase["phase"],
        "phase_number": current_phase + 1,
        "all_phases": len(final_roadmap),
        "step_title": step["title"],
        "tasks": step["tasks"],
        "resource_query": step["resource_query"]
    }
    
    
    return templates.TemplateResponse(request, 'today_focus.html', {
        "todays_data": todays_data,
        "is_logged_in": True
    })