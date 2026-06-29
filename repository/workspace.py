import requests
import os
import json


# Maps the user's PRIMARY GOAL (q1) to a concrete instruction that shapes
# the whole roadmap. This is what makes placement vs startup produce
# genuinely different roadmaps instead of one generic path.
intent_to_focus = {
    "Placement / interview prep": (
        "PRIORITIZE DATA STRUCTURES AND ALGORITHMS: arrays, strings, linked lists, "
        "stacks, queues, trees, graphs, sorting, searching, recursion, and dynamic "
        "programming, plus time and space complexity. Every phase must include DSA "
        "practice and interview-style problems. Building full apps is SECONDARY. "
        "STRUCTURE: Phase 1 = language fundamentals, Phases 2 to 5 = progressively "
        "harder DSA topics, final phase = mock interviews and revision. Projects "
        "should be DSA implementations (build a hash map, a sorting visualizer, etc.), "
        "NOT web apps. Endgame: crack technical placement interviews."
    ),
    "Launch a startup": (
        "PRIORITIZE SHIPPING REAL CODE FAST: full-stack basics, building an MVP, "
        "connecting a database, adding simple auth, and deploying live early. Keep "
        "DSA and heavy theory minimal. STRUCTURE: Phase 1 = language basics, Phase 2 "
        "= build and deploy something small but real, later phases = add database, "
        "auth, and polish. Projects must be real shippable apps, NOT algorithm "
        "exercises. Endgame: a launched, working product they built themselves."
    ),
    "Build my own product": (
        "PRIORITIZE PRACTICAL BUILDING: making real things end to end with the tools "
        "to bring their own ideas to life. Light DSA, heavy hands-on projects. "
        "Projects should be things they would actually want to use or show off. "
        "Endgame: confidently build whatever they imagine."
    ),
    "Get a tech job": (
        "BALANCE job-ready building skills with enough DSA to pass interviews. Include "
        "real portfolio projects AND core algorithms and data structures. Add resume "
        "and interview prep in later phases. Endgame: a hireable developer with both "
        "a portfolio and interview skills."
    ),
    "Just for fun": (
        "KEEP IT LIGHT AND PLAYFUL: fun, small, satisfying projects at a gentle pace "
        "with quick visible wins and zero pressure. No interview grind, no heavy "
        "theory. Endgame: enjoyment, curiosity, and the joy of making things work."
    ),
}


def ai(checked_answers, focus):
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"""
You are an elite coding mentor who has personally helped thousands of beginners go from zero to their goal. You are honest, specific, warm, and you talk like a real coach who believes in this person, not like a textbook.

STUDENT PROFILE:
- PRIMARY GOAL (why they learn): {checked_answers.q1}
- What they want to build: {checked_answers.q2}
- Coding experience: {checked_answers.q3}
- Time available daily: {checked_answers.q4}
- Biggest challenge: {checked_answers.q5}

THE MOST IMPORTANT INSTRUCTION (this shapes the ENTIRE roadmap):
{focus}
The PRIMARY GOAL above DOMINATES every decision. Every phase, project, task, and resource must serve it. Do NOT produce a generic roadmap. Two learners with the same "what they want to build" but different PRIMARY GOALS must get clearly DIFFERENT roadmaps. Let the goal lead.

CORE RULES:
1. LANGUAGE (CRITICAL): Choose ONE primary programming language that best fits their PRIMARY GOAL and what they want to build.
   - For placement prep: DEFAULT to C++ (most common DSA/interview language). Use Java only if their interest is clearly web or enterprise.
   - For Data Analysis: use Python (with SQL mentioned as a companion).
   - For Websites & Web Apps: use JavaScript.
   - For AI & Smart Systems: use Python.
   - For Phone Apps: use Kotlin (Android) or Dart/Flutter.
   - For Games: use C++ or C#.
   - For startups/products: prefer Python or JavaScript (fast to ship).
   When PRIMARY GOAL is placement, the placement language rule wins over the domain.
   State the chosen language clearly in Phase 1. Use this SAME language in EVERY phase, step, task, and resource_query. A roadmap that does not name a specific language, or switches languages, is INVALID. Every phase resource_query MUST contain the language name.
2. FRONT-LOAD THE REWARD: The learner must build or solve something they can SEE working and feel proud of within the first 1 to 2 phases. Do not save all the exciting parts for the end. Early small wins are what keep beginners going, since most people quit early.
3. TASKS MUST BE TINY AND CONCRETE: Each practice task must be doable in ONE short sitting (15 to 30 minutes) and specific enough that the learner knows exactly what to do. BAD: "practice using variables". GOOD: "write a program that stores your name and age in two variables and prints My name is X and I am Y". Never use vague verbs like practice, explore, or understand on their own.
4. Be brutally realistic about timelines. Never promise job-ready in a few weeks.
5. Calibrate difficulty to their experience. If they never coded, the first step is genuinely absolute-beginner level.
6. Pace phases to their daily time. Directly address their stated biggest challenge in the roadmap (for example, if they get overwhelmed, keep steps small and reassure them).
7. Write like a coach: each why_this_matters must be personal and encouraging, connecting the phase to THEIR specific goal, not generic motivation.
8. Create 5 to 7 phases. Calibrate steps per phase to daily time: 1 hour = 3 to 4 steps, 2 hours = 4 to 5 steps, 3 hours = 5 to 6 steps, 4 or more hours = 7 to 8 steps.
9. For EACH phase provide a resource_query: a detailed, specific YouTube search query that covers the ENTIRE phase topic. It must include the chosen language, the phase subject, and beginner-friendly keywords so the learner finds the best tutorial playlist or full course for that phase. BAD: "python tutorial". GOOD: "python functions and scope complete beginner tutorial full course". The query must be 6 to 10 words and always include the language name.
10. For EACH step provide:
    - a clear, specific title
    - exactly 3 practice tasks following RULE 3 (tiny, concrete, one sitting)
11. Each phase has ONE real project relevant to their PRIMARY GOAL and buildable in the chosen language.

FORMATTING:
- Return ONLY a valid JSON array. No markdown. No code fences. No explanation before or after.
- No apostrophes in any text. Use plain words.

Format:
[
  {{
    "phase": "Phase name",
    "goal": "What the user will achieve",
    "why_this_matters": "One personal, encouraging sentence tied to their goal",
    "resource_query": "detailed 6-10 word YouTube search query for this full phase, always including the language name, e.g. python functions and scope complete beginner tutorial full course",
    "steps": [
      {{
        "title": "Step title",
        "tasks": ["tiny concrete task 1", "tiny concrete task 2", "tiny concrete task 3"]
      }}
    ],
    "project": "One real project relevant to their goal, built in the chosen language",
    "avoid": ["trap 1", "trap 2"],
    "duration": "realistic time estimate"
  }}
]
"""

    api_key = os.getenv("GROQ_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a coding mentor."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 8000
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()
        print("finish_reason:", data['choices'][0].get('finish_reason'))
        return data['choices'][0]["message"]["content"]
    except Exception as e:
        print(f"AI call failed - {e}")
        raise RuntimeError("AI roadmap generation failed. Please try again.")






def validate_answers(phase_name: str, topic: str, questions: list, answers: list) -> bool:
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    qa_text = "\n".join(
        f"Q{i+1}: {q}\nA{i+1}: {answers[i] if i < len(answers) else '(no answer)'}"
        for i, q in enumerate(questions)
    )
    prompt = (
        f"You are evaluating a coding student's quiz answers.\n\n"
        f"Phase: {phase_name}\nTopic: {topic}\n\n"
        f"{qa_text}\n\n"
        f"Did the student show basic understanding of the topic? "
        f"Accept only if the answer demonstrates actual understanding of the concept, not just effort."
        f"Reject empty answers, 'I don't know', completely off-topic, or zero understanding.\n"
        f"Respond with only one word: PASS or FAIL"
    )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a strict but fair quiz evaluator. Respond only with PASS or FAIL."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 10
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        result = r.json()['choices'][0]['message']['content'].strip().upper()
        return "PASS" in result
    except Exception as e:
        print(f"validate_answers failed: {e}")
        return False


def tutor_chat_reply(phase_name: str, topic: str, history: list, message: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    system_prompt = (
        f"You are a patient, encouraging coding tutor. "
        f"The student is learning: {phase_name} (topic: {topic}). "
        f"They didn't pass the quiz for this phase. Help them understand through conversation. "
        f"Keep answers short and clear — 2-4 sentences max. Use simple examples. "
        f"After they seem to understand, encourage them to go back and try the quiz again."
    )
    messages = [{"role": "system", "content": system_prompt}] + history[-10:] + [{"role": "user", "content": message}]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 400
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"tutor_chat_reply failed: {e}")
        return "Sorry, I'm having trouble right now. Please try again."


def generate_questions(phase_name: str, topic: str) -> list:
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = (
        f"A student just finished watching a tutorial video on this coding topic.\n\n"
        f"Phase: {phase_name}\n"
        f"Topic: {topic}\n\n"
        f"Generate exactly 2 short-answer questions to verify they understood the key concepts. "
        f"Make questions specific, answerable in 1-2 sentences, and test real understanding.\n"
        f"Return ONLY a valid JSON array of 2 strings. No markdown, no explanation.\n"
        f'Example: ["What is the difference between X and Y?", "Write one line of code that does Z"]'
    )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a concise coding coach who creates quiz questions. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        content = r.json()['choices'][0]['message']['content'].strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        questions = json.loads(content.strip())
        if isinstance(questions, list) and len(questions) >= 2:
            return questions[:3]
    except Exception as e:
        print(f"generate_questions failed: {e}")
    return [
        "What was the main concept covered in this phase?",
        "Describe one practical thing you can now do that you couldn't do before."
    ]