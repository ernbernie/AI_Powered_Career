from pydantic import BaseModel, constr

class UserGoalInput(BaseModel):
    five_year_goal: constr(strip_whitespace=True, min_length=10)
    location: constr(strip_whitespace=True, min_length=2) 