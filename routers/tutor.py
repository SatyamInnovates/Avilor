from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from routers.auth import supabase
from repository.workspace import tutor_chat_reply
from collections import defaultdict
from time import time
import json

router = APIRouter()
templates = Jinja2Templates(directory='template')

_chat_windows: dict = defaultdict(list)
_WINDOW = 60
_MAX_MSGS = 8


def _is_rate_limited(user_id: str) -> bool:
    now = time()
    _chat_windows[user_id] = [t for t in _chat_windows[user_id] if now - t < _WINDOW]
    if len(_chat_windows[user_id]) >= _MAX_MSGS:
        return True
    _chat_windows[user_id].append(now)
    return False


@router.get("/workspace/tutor")
async def show_tutor(request: Request, phase: int = 0, step: str = ""):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

    phase_name = f'Phase {phase + 1}'
    topic = 'programming concepts'
    try:
        result = supabase.table('roadmaps').select('roadmap_content').eq('user_id', user_id).order('created_at', desc=True).execute()
        if result.data:
            content = result.data[0]['roadmap_content'].strip().replace("```json", "").replace("```", "").strip()
            roadmap = json.loads(content)
            p = roadmap[phase]
            phase_name = p.get('phase', phase_name)
            topic = p.get('resource_query') or phase_name
    except Exception as e:
        print(f"show_tutor: could not load phase: {e}")

    chat_history = []
    try:
        chat_data = supabase.table('tutor_chats').select('messages').eq('user_id', user_id).eq('phase_index', phase).execute()
        if chat_data.data:
            chat_history = chat_data.data[0].get('messages') or []
    except Exception as e:
        print(f"show_tutor: could not load chat history: {e}")

    return templates.TemplateResponse(request, 'tutor.html', {
        "is_logged_in": True,
        "phase_index": phase,
        "phase_name": phase_name,
        "topic": step if step else topic,
        "step_topic": step,
        "chat_history": chat_history
    })


@router.post("/workspace/tutor/chat")
async def tutor_chat(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse({"error": "not logged in"}, status_code=401)

    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        return JSONResponse({"error": "invalid token"}, status_code=401)

    if _is_rate_limited(user_id):
        return JSONResponse({"error": "rate_limit", "reply": "Slow down — max 8 messages per minute. Read the reply first."}, status_code=429)

    body = await request.json()
    message = body.get('message', '').strip()
    full_history = body.get('history', [])
    phase_name = body.get('phase_name', '')
    topic = body.get('topic', '')
    phase_index = int(body.get('phase_index', 0))

    if not message:
        return JSONResponse({"error": "empty message"}, status_code=400)

    reply = tutor_chat_reply(phase_name, topic, full_history[-10:], message)

    try:
        new_history = full_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply}
        ]
        supabase.table('tutor_chats').upsert({
            "user_id": user_id,
            "phase_index": phase_index,
            "messages": new_history
        }, on_conflict="user_id,phase_index").execute()
    except Exception as e:
        print(f"tutor_chat: could not save history: {e}")

    return JSONResponse({"reply": reply})
