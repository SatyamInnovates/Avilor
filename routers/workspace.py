from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from routers.auth import supabase
import json


router = APIRouter()
templates = Jinja2Templates(directory='template')


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

    is_logged_in = True
    return templates.TemplateResponse(request, 'workspace.html', {"roadmap": final_roadmap, "role": user_role, "is_logged_in": is_logged_in})


