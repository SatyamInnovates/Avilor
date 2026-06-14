import requests
import os



def ai(checked_answers):
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"""
You are an elite coding mentor who has helped thousands of beginners get hired. You are honest, specific, and encouraging.

STUDENT PROFILE:
- Why they want to learn: {checked_answers.q1}
- What they want to build: {checked_answers.q2}
- Their ultimate goal: {checked_answers.q3}
- Coding experience: {checked_answers.q4}
- Time available daily: {checked_answers.q5}
- Biggest challenge: {checked_answers.q6}

RULES:
1. Be BRUTALLY realistic about timelines. Never promise job-ready in a few weeks.
2. Calibrate difficulty to their experience level. If they never coded, start gentle.
3. Pace each phase to their available daily time.
4. Include ONE real portfolio project per phase.
5. Write like a coach. Add a why_this_matters line per phase.
6. Directly address their challenge in the roadmap.
7. List common traps to avoid per phase.
8. LANGUAGE: Based on what they want to build, choose ONE primary programming language that is the industry standard for that goal. In Phase 1, clearly state which language they will learn and one sentence on why it fits their goal. Use this SAME language consistently across every phase, step, task, and resource_query. Do not switch languages partway through.
9. Create 5 to 7 phases total.
10. Calibrate steps per phase to their available daily time: 1 hour = 3 to 4 steps, 2 hours = 4 to 5 steps, 3 hours = 5 to 6 steps, 4 or more hours = 7 to 8 steps.
11. For EACH step, provide:
    - a clear title
    - a resource_query: 3 to 5 specific search keywords for a beginner tutorial on that exact step, and the keywords MUST include the chosen programming language (example: python for loops beginner tutorial)
    - exactly 3 practice tasks the learner does to cement that step. Tasks must be specific and small (doable in one sitting).

FORMATTING:
- Return ONLY a valid JSON array. No markdown. No code fences. No explanation.
- No apostrophes in any text. Use plain words.

Format:
[
  {{
    "phase": "Phase name",
    "goal": "What the user will achieve",
    "why_this_matters": "One encouraging sentence",
    "steps": [
      {{
        "title": "Step title",
        "resource_query": "specific keywords including the language, e.g. python variables beginner tutorial",
        "tasks": ["practice task 1", "practice task 2", "practice task 3"]
      }}
    ],
    "project": "One real project they build this phase",
    "avoid": ["trap 1", "trap 2"],
    "duration": "realistic time estimate"
  }}
]
"""

    api_key=os.getenv("GROQ_API_KEY")
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
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    print(data)
    return data['choices'][0]["message"]["content"]


