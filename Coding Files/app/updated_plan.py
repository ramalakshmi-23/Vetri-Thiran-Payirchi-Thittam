from .config import WORKOUT_MODEL
from .gemini_client import get_client
from .schemas import UserInput, WorkoutPlan


SYSTEM_INSTRUCTION = """
You are FitBuddy updating an existing general wellness workout plan.
Make only safe, reasonable changes based on the user's feedback.
Never recommend dangerous challenges, extreme exercise, starvation, purging,
unsafe supplements, or appearance-focused body judgment.
For minors, keep recommendations moderate and age-appropriate.
Return exactly 7 days and only data matching the requested JSON schema.
"""


def update_workout_plan(
    user: UserInput,
    original_plan: str,
    feedback: str,
) -> WorkoutPlan:
    from google.genai import types
    prompt = f"""
Update this user's 7-day wellness plan.

User:
- Name: {user.username}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Intensity: {user.intensity}

User feedback:
{feedback}

Original plan:
{original_plan}

Preserve useful parts of the original plan while applying the feedback.
Return exactly 7 days.
"""

    response = get_client().models.generate_content(
        model=WORKOUT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=WorkoutPlan,
        ),
    )

    if getattr(response, "parsed", None):
        return response.parsed

    return WorkoutPlan.model_validate_json(response.text)
