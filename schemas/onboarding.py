from pydantic import BaseModel
from typing import Literal

class OnboardingAnswers(BaseModel):
    q1 : Literal["Placement / interview prep", "Get a tech job", "Build my own product", "Launch a startup", "Just for fun"]
    q2 : Literal["Websites & Web Apps", "Phone Apps", "AI & Smart Systems", "Data Analysis", "Games", "Server & Infrastructure"]
    q3 : Literal["Never written any code", "Completed online tutorials", "Built a few small projects", "Coding regularly for months"]
    q4 : Literal["30 minutes", "1 hour", "2 hours", "3+ hours"]
    q5 : Literal["Don't know where to start", "Get overwhelmed by too much info", "Struggle to stay motivated", "Limited time available", "Get stuck on problems and give up"]
       