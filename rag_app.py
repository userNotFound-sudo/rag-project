import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Fail fast if missing
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

# Create FastAPI app
app = FastAPI()


class QueryRequest(BaseModel):
    question: str


def validate_user_input(text: str):
    if text is None or text.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Question is too short")

    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Question is too long")


def validate_model_output(text: str):
    if text is None or text.strip() == "":
        raise HTTPException(status_code=500, detail="AI returned an empty response")

    if len(text) < 10:
        raise HTTPException(status_code=500, detail="AI response is too short")


def review_model_output(client, original_answer: str):
    review_prompt = f"""
You are reviewing an AI-generated response.

Your job:
- If the response is unclear, incomplete, or poorly written, improve it.
- If the response is already good, return it unchanged.

AI response to review:
{original_answer}
"""
    review_result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=review_prompt,
    )
    return getattr(review_result, "text", None)

# Root endpoint (basic test)
@app.get("/")
def root():
    return {"message": "RAG app is running"}

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok", "api_key_loaded": True}

# Week 5/6: Gemini endpoint with multi-step execution.
# Note: All Gemini logic lives inside this function.
@app.get("/test-gemini")
def test_gemini():
    try:
        # Import inside the function to keep Week 4 scaffolding unchanged.
        from google import genai

        client = genai.Client(api_key=api_key)
        model = "gemini-2.5-flash"
        topic = "what a large language model is"

        # Step 1: Generate a short outline (intermediate result).
        outline_prompt = (
            f"Create a short bullet-point outline (3-5 points) explaining {topic}."
        )
        outline_result = client.models.generate_content(
            model=model,
            contents=outline_prompt,
        )
        outline = getattr(outline_result, "text", None)
        if not outline:
            raise RuntimeError("Gemini returned an empty outline in step 1.")

        # Safe server-side inspection only; not returned to the client.
        print(f"[test_gemini] Step 1 outline generated ({len(outline)} chars)")

        # Step 2: Expand the outline into a full response.
        expand_prompt = (
            f"Using this outline:\n{outline}\n\n"
            f"Write one clear paragraph explaining {topic}."
        )
        final_result = client.models.generate_content(
            model=model,
            contents=expand_prompt,
        )
        response_text = getattr(final_result, "text", None)
        if not response_text:
            raise RuntimeError("Gemini returned an empty response in step 2.")

        return {"response": response_text}
    except Exception:
        # Raise a clear error without exposing secrets.
        raise RuntimeError(
            "Gemini request failed. Verify GEMINI_API_KEY is set, "
            "the `google-genai` package is installed, "
            "and the server has network access."
        )


@app.post("/query")
def query_ai(request: QueryRequest):
    validate_user_input(request.question)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        primary_result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.question,
        )
        raw_answer = getattr(primary_result, "text", None)

        validate_model_output(raw_answer)

        reviewed_answer = review_model_output(client, raw_answer)
        validate_model_output(reviewed_answer)

        return {
            "question": request.question,
            "answer": reviewed_answer,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Query processing failed. Verify GEMINI_API_KEY is set, "
                "the `google-genai` package is installed, "
                "and the server has network access."
            ),
        )