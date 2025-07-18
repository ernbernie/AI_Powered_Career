import pytest
from pydantic import ValidationError
from backend.models import UserGoalInput, RoadmapOutput, YearlyGoal, QuarterlyGoal, SmartGoal

def test_user_goal_input_valid():
    data = {"five_year_goal": "Become a senior engineer at a top company.", "location": "Tucson, AZ"}
    obj = UserGoalInput(**data)
    assert obj.five_year_goal == data["five_year_goal"]
    assert obj.location == data["location"]

def test_user_goal_input_invalid_goal():
    data = {"five_year_goal": "Too short", "location": "Tucson, AZ"}
    with pytest.raises(ValidationError):
        UserGoalInput(**data)

def test_user_goal_input_invalid_location():
    data = {"five_year_goal": "A valid long enough goal.", "location": "Tucson Arizona"}
    with pytest.raises(ValidationError):
        UserGoalInput(**data)

def test_roadmap_output_valid():
    yearly_goals = [
        YearlyGoal(year=1, year_goal="Goal 1", quarterly_smart_goals=[
            QuarterlyGoal(quarter="Q1", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
            QuarterlyGoal(quarter="Q2", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
            QuarterlyGoal(quarter="Q3", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
            QuarterlyGoal(quarter="Q4", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
        ]),
        YearlyGoal(year=2, year_goal="Goal 2"),
        YearlyGoal(year=3, year_goal="Goal 3"),
        YearlyGoal(year=4, year_goal="Goal 4"),
        YearlyGoal(year=5, year_goal="Goal 5"),
    ]
    data = {"five_year_goal": "A valid five year goal.", "location": "Tucson, AZ", "yearly_goals": yearly_goals}
    obj = RoadmapOutput(**data)
    assert obj.five_year_goal == data["five_year_goal"]
    assert obj.location == data["location"]
    assert len(obj.yearly_goals) == 5

def test_roadmap_output_invalid_years():
    # Only 4 years instead of 5
    yearly_goals = [
        YearlyGoal(year=1, year_goal="Goal 1", quarterly_smart_goals=[
            QuarterlyGoal(quarter="Q1", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
            QuarterlyGoal(quarter="Q2", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
            QuarterlyGoal(quarter="Q3", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
            QuarterlyGoal(quarter="Q4", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
        ]),
        YearlyGoal(year=2, year_goal="Goal 2"),
        YearlyGoal(year=3, year_goal="Goal 3"),
        YearlyGoal(year=4, year_goal="Goal 4"),
    ]
    data = {"five_year_goal": "A valid five year goal.", "location": "Tucson, AZ", "yearly_goals": yearly_goals}
    with pytest.raises(ValidationError):
        RoadmapOutput(**data)

def test_roadmap_output_invalid_quarters():
    # Year 1 missing quarterly_smart_goals
    yearly_goals = [
        YearlyGoal(year=1, year_goal="Goal 1", quarterly_smart_goals=[
            QuarterlyGoal(quarter="Q1", goal="Quarter goal", smart=SmartGoal(S="s", M="m", A="a", R="r", T="t")),
        ]),
        YearlyGoal(year=2, year_goal="Goal 2"),
        YearlyGoal(year=3, year_goal="Goal 3"),
        YearlyGoal(year=4, year_goal="Goal 4"),
        YearlyGoal(year=5, year_goal="Goal 5"),
    ]
    data = {"five_year_goal": "A valid five year goal.", "location": "Tucson, AZ", "yearly_goals": yearly_goals}
    with pytest.raises(ValidationError):
        RoadmapOutput(**data) 