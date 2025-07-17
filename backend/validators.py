import re

def validate_goal(goal: str) -> str:
    goal = goal.strip()
    if len(goal) < 10:
        raise ValueError("5-year goal must be at least 10 characters long.")
    return goal

def validate_location(location: str) -> str:
    location = location.strip()
    # Enforce 'City, ST' format (US only)
    pattern = r'^[A-Za-z\s\-]{2,},\s*[A-Z]{2}$'
    if not re.match(pattern, location):
        raise ValueError('Location must be in the format "City, ST" (e.g., "Tucson, AZ")')
    return location