from fastapi import Request


def get_questions():
    questions = {
    "q1": {
        "text": "Why do you want to learn coding?",
        "options": ["Secure a tech job", "Build my own projects", "Switch careers to tech", "Explore and learn", "Launch a startup"]
    },
    "q2": {
    "text": "What interests you most to build?",
    "options": ["Websites & Web Apps", "Phone Apps", "AI & Smart Systems", "Data Analysis", "Games", "Server & Infrastructure"]
    }   ,
    "q3": {
        "text": "What's your ultimate goal?",
        "options": ["Work as a freelancer", "Get hired at a company", "Launch my own product", "Learn for personal growth", "Teach others to code"]
    },
    "q4": {
        "text": "What's your coding experience?",
        "options": ["Never written any code", "Completed online tutorials", "Built a few small projects", "Coding regularly for months"]
    },
    "q5": {
        "text": "How much time can you dedicate daily?",
        "options": ["30 minutes", "1 hour", "2 hours", "3+ hours"]
    },
    "q6": {
        "text": "What's your biggest challenge right now?",
        "options": ["Don't know where to start", "Get overwhelmed by too much info", "Struggle to stay motivated", "Limited time available", "Get stuck on problems and give up"]
    }
}
    return questions