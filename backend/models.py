# backend/models.py
from typing import List, Optional
from pydantic import BaseModel, Field, constr, validator

# ---------- Form input (already used elsewhere) ----------
class UserGoalInput(BaseModel):
    five_year_goal: constr(strip_whitespace=True, min_length=10)
    location:       constr(strip_whitespace=True, min_length=2)

# ---------- Road‑map output from the LLM ----------
class SmartGoal(BaseModel):
    S: str = ""
    M: str = ""
    A: str = ""
    R: str = ""
    T: str = ""

class QuarterlyGoal(BaseModel):
    quarter: str
    goal: str
    smart: SmartGoal

class YearlyGoal(BaseModel):
    year: int
    year_goal: str
    quarterly_smart_goals: Optional[List[QuarterlyGoal]] = None  # only required for year 1

    # enforce 4 quarter goals when year == 1
    @validator("quarterly_smart_goals", always=True)
    def _validate_quarters(cls, v, values):
        if values.get("year") == 1:
            if not v or len(v) != 4:
                raise ValueError("Year 1 must contain exactly 4 quarterly_smart_goals")
        return v

class RoadmapOutput(BaseModel):
    five_year_goal: str
    location: str
    yearly_goals: List[YearlyGoal] = Field(..., min_items=5, max_items=5)

    # enforce years 1‑5 present exactly once
    @validator("yearly_goals")
    def _validate_year_list(cls, v):
        years = sorted(g.year for g in v)
        if years != [1, 2, 3, 4, 5]:
            raise ValueError("yearly_goals must include years 1–5 exactly once")
        return v
