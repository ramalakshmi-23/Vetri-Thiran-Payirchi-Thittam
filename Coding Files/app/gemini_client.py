from functools import lru_cache

from .config import GEMINI_API_KEY


class GeminiConfigurationError(RuntimeError):
    pass


@lru_cache
def get_client():
    if not GEMINI_API_KEY:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is missing. Add it to the .env file and restart the server."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise GeminiConfigurationError(
            "The Google GenAI SDK is not installed. Run: python -m pip install -r requirements.txt"
        ) from exc

    return genai.Client(api_key=GEMINI_API_KEY)
