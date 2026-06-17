import requests
import os


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
   State the chosen language clearly in Phase 1. Use this SAME language in EVERY phase, step, task, and resource_query. A roadmap that does not name a specific language, or switches languages, is INVALID. Every resource_query MUST contain the language name.
2. FRONT-LOAD THE REWARD: The learner must build or solve something they can SEE working and feel proud of within the first 1 to 2 phases. Do not save all the exciting parts for the end. Early small wins are what keep beginners going, since most people quit early.
3. TASKS MUST BE TINY AND CONCRETE: Each practice task must be doable in ONE short sitting (15 to 30 minutes) and specific enough that the learner knows exactly what to do. BAD: "practice using variables". GOOD: "write a program that stores your name and age in two variables and prints My name is X and I am Y". Never use vague verbs like practice, explore, or understand on their own.
4. Be brutally realistic about timelines. Never promise job-ready in a few weeks.
5. Calibrate difficulty to their experience. If they never coded, the first step is genuinely absolute-beginner level.
6. Pace phases to their daily time. Directly address their stated biggest challenge in the roadmap (for example, if they get overwhelmed, keep steps small and reassure them).
7. Write like a coach: each why_this_matters must be personal and encouraging, connecting the phase to THEIR specific goal, not generic motivation.
8. Create 5 to 7 phases. Calibrate steps per phase to daily time: 1 hour = 3 to 4 steps, 2 hours = 4 to 5 steps, 3 hours = 5 to 6 steps, 4 or more hours = 7 to 8 steps.
9. For EACH step provide:
   - a clear, specific title
   - a resource_query: 3 to 5 search keywords for a beginner YouTube tutorial on THAT exact step, ALWAYS including the chosen language (example: python for loops beginner tutorial)
   - exactly 3 practice tasks following RULE 3 (tiny, concrete, one sitting)
10. Each phase has ONE real project relevant to their PRIMARY GOAL and buildable in the chosen language.

FORMATTING:
- Return ONLY a valid JSON array. No markdown. No code fences. No explanation before or after.
- No apostrophes in any text. Use plain words.

Format:
[
  {{
    "phase": "Phase name",
    "goal": "What the user will achieve",
    "why_this_matters": "One personal, encouraging sentence tied to their goal",
    "steps": [
      {{
        "title": "Step title",
        "resource_query": "specific keywords including the language, e.g. python variables beginner tutorial",
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