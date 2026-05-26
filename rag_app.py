import os
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API key loaded successfully"}
