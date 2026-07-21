# monitoring.py
# -------------
# This file monitors the quality of our RAG app's responses.
#
# What is hallucination?
# Even when we give an LLM context documents, it sometimes generates
# information that isn't actually in those documents. It "fills in the gaps"
# with plausible-sounding but unverified facts. This is called hallucination.
#
# How do we detect it?
# We use a technique called "LLM-as-judge": we send the answer AND the
# source documents back to Gemini and ask it to evaluate whether the answer
# is actually supported by the context. This is a common pattern in
# production RAG systems.

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)


def check_hallucination(answer, context_docs):
    """
    Ask Gemini to evaluate whether the generated answer is grounded in
    the source documents that were retrieved.
    """
    try:
        context = "\n\n".join(
            [f"Document {i+1}: {doc}" for i, doc in enumerate(context_docs)]
        )

        prompt = f"""
You are evaluating whether an AI answer is supported by retrieved documents.

Retrieved Documents:
{context}

Generated Answer:
{answer}

Classify the answer using exactly ONE of these words:

GROUNDED - The answer contains claims directly supported by the retrieved documents.

PARTIAL - Some claims are supported, but some information goes beyond the retrieved documents.

HALLUCINATED - The answer contains unsupported information not found in the documents.

NO_CONTEXT - The documents do not contain enough information to answer, or the AI refused to answer because evidence was missing.

Important rules:
- If the answer says it cannot answer, do NOT mark it as GROUNDED.
- If the retrieved documents are empty or unrelated, use NO_CONTEXT.
- Do not assume outside knowledge is supported.

Respond with exactly one word:
GROUNDED
PARTIAL
HALLUCINATED
NO_CONTEXT
"""

        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0
            ),
        )

        verdict = response.text.strip().upper()

        if verdict not in [
            "GROUNDED",
            "PARTIAL",
            "HALLUCINATED",
            "NO_CONTEXT"
        ]:
            verdict = "PARTIAL"

        if verdict == "GROUNDED":
            warning = ""
        elif verdict == "PARTIAL":
            warning = (
                "Note: This answer may include some information beyond the provided sources."
            )
        elif verdict == "NO_CONTEXT":
            warning = (
                "Warning: There was not enough information in the retrieved documents."
            )
        else:
            warning = (
                "Warning: This answer may contain information not found in the source documents."
            )

        return {
            "verdict": verdict,
            "is_grounded": verdict == "GROUNDED",
            "warning": warning,
        }

    except Exception as e:
        print("Grounding check error:", e)
        return {
            "verdict": "UNKNOWN",
            "is_grounded": False,
            "warning": "Grounding check failed.",
        }


def calculate_confidence(distances):
    """
    Convert ChromaDB similarity distances into a 0–1 confidence score.

    Args:
        distances: A list of L2 distance values from ChromaDB.
                   0.0 = identical vectors, 2.0 = completely different.

    Returns:
        A float between 0.0 (not confident) and 1.0 (very confident).
    """
    if not distances:
        return 0.0

    avg_distance = sum(distances) / len(distances)

    confidence = max(0.0, 1.0 - (avg_distance / 2.0))

    return round(confidence, 2)
