import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from .env file
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Fail fast if missing
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

# Create FastAPI app
app = FastAPI()

# Root endpoint (basic test)
@app.get("/")
def root():
    return {"message": "RAG app is running"}

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok", "api_key_loaded": True}

# Week 5: Gemini connectivity test scaffold.
# Note: All Gemini logic lives inside this function.
@app.get("/test-gemini")
def test_gemini():
    try:
        # Import inside the function to keep Week 4 scaffolding unchanged.
        # The older `google.generativeai` SDK is deprecated and may not support
        # current Gemini model names for all keys; use the newer `google.genai`.
        from google import genai

        client = genai.Client(api_key=api_key)
        prompt = "Explain what a large language model is in one paragraph."

        # Create a model and generate content with a simple hardcoded prompt.
        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        response_text = getattr(result, "text", None)
        if not response_text:
            raise RuntimeError("Gemini returned an empty response.")

        return {"response": response_text}
    except Exception:
        # Raise a clear error without exposing secrets.
        raise RuntimeError(
            "Gemini request failed. Verify GEMINI_API_KEY is set, "
            "the `google-genai` package is installed, "
            "and the server has network access."
        )