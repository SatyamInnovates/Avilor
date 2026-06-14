from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from routers.auth import supabase
import json


router = APIRouter()
templates = Jinja2Templates(directory='template')


@router.get("/workspace")
def show_workspace(request: Request):
    
    token = request.cookies.get("access_token")
    user = supabase.auth.get_user(token)
    user_id = user.user.id

    result = supabase.table('roadmaps').select('roadmap_content , role').eq('user_id', user_id).order('created_at', desc=True).execute()
    
    if result.data:
        fetched_answer = result.data[0]['roadmap_content']
        print('answer is here')
        try:
            pre_roadmap = fetched_answer.strip().replace("```json","").replace("```","").strip()
            final_roadmap = json.loads(pre_roadmap)
            user_role = result.data[0].get('role', 'Developer') if result.data else None
        except Exception as e:
            print(f"JSON parse failed - {e}")
            final_roadmap = None
    else:
        final_roadmap = None
    is_logged_in = request.cookies.get("access_token") is not None
    return templates.TemplateResponse(request, 'workspace.html', {"roadmap": final_roadmap,"role":user_role , "is_logged_in": is_logged_in})


