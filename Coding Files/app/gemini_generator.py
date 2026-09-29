from .config import WORKOUT_MODEL
from .gemini_client import get_client
from .schemas import UserInput, WorkoutPlan


SYSTEM_INSTRUCTION = """
You are FitBuddy, a cautious fitness and wellness planning assistant.
Create general, age-appropriate, non-medical exercise guidance.
Never recommend dangerous challenges, extreme exercise, starvation, purging,
unsafe supplements, or rapid weight-loss methods. Do not judge appearance.
For minors, keep recommendations moderate, emphasize enjoyment, rest,
hydration, and adult/qualified-professional support when appropriate.
The user should stop if they feel pain, dizziness, faintness, or unusual symptoms.
"""


def generate_workout_gemini(user: UserInput) -> WorkoutPlan:
    from google.genai import types
    prompt = f"""
Create a personalized 7-day wellness-oriented workout plan.

User:
- Name: {user.username}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

Requirements:
- Exactly 7 days.
- Each day needs a focus, 5-10 minute warm-up, exercises, and cool-down/recovery.
- Exercise entries need name, sets, reps_or_duration, and rest.
- Keep the plan practical for a general web application.
- Do not prescribe medical treatment.
- Do not make body-size judgments or promise a specific weight change.
- Include rest/recovery days where appropriate.
- Return only data matching the requested JSON schema.
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
