"""
VEDA — Vertex AI Helper
Central wrapper for all Gemini API calls.
"""
import time
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from utils.config import PROJECT_ID, LOCATION

_model = None

def _get_model() -> GenerativeModel:
    global _model
    if _model is None:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        _model = GenerativeModel("gemini-2.5-flash")
    return _model

def ask_gemini(prompt: str, temperature: float = 0.2, max_tokens: int = 8192) -> str:
    """Send a prompt to Gemini with retry on rate limit."""
    model = _get_model()
    config = GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    for attempt in range(3):
        try:
            response = model.generate_content(prompt, generation_config=config)
            # Handle MAX_TOKENS or blocked response gracefully
            try:
                return response.text
            except ValueError:
                # Extract partial text if available
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            return part.text
                return "Analysis completed with partial results."
        except Exception as e:
            if "429" in str(e) or "Resource exhausted" in str(e):
                wait = 30 * (attempt + 1)
                print(f"[Gemini] Rate limited. Waiting {wait}s (retry {attempt+1}/3)...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Gemini rate limit exceeded after 3 retries")