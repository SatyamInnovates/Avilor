from pydantic import BaseModel
from typing import Literal

class OnboardingAnswers(BaseModel):
    q1 : Literal["Secure a tech job", "Build my own projects", "Switch careers to tech", "Explore and learn", "Launch a startup"]
    q2 : Literal["Websites & Web Apps", "Phone Apps", "AI & Smart Systems", "Data Analysis", "Games", "Server & Infrastructure"]
    q3 : Literal["Work as a freelancer", "Get hired at a company", "Launch my own product", "Learn for personal growth", "Teach others to code"]
    q4 : Literal["Never written any code", "Completed online tutorials", "Built a few small projects", "Coding regularly for months"]
    q5 : Literal["30 minutes", "1 hour", "2 hours", "3+ hours"]
    q6 : Literal["Don't know where to start", "Get overwhelmed by too much info", "Struggle to stay motivated", "Limited time available", "Get stuck on problems and give up"]
       