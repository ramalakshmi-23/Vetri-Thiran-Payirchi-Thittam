from .config import TIP_MODEL
from .gemini_client import get_client
from .schemas import NutritionTip


def generate_nutrition_tip_with_flash(goal: str, age: int) -> NutritionTip:
    from google.genai import types
    prompt = f"""
Give one concise nutrition/recovery tip for a FitBuddy user.

Goal: {goal}
Age: {age}

Requirements:
- Focus on balanced food, hydration, sleep, and recovery.
- Do not recommend restrictive dieting, fasting, diet pills, unsafe supplements,
  calorie targets, or rapid weight-loss methods.
- If the user is a minor, keep the advice general and encourage support from a
  parent/guardian or qualified health professional for individualized nutrition.
- Return only JSON matching the schema.
"""

    response = get_client().models.generate_content(
        model=TIP_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NutritionTip,
        ),
    )

    if getattr(response, "parsed", None):
        return response.parsed

    return NutritionTip.model_validate_json(response.text)
