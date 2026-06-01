# RAG Project

This repository contains my Retrieval-Augmented Generation (RAG) project for the GenAI Secure Coding course.

This project will be built incrementally each week.


## Git Commands Used So Far

- git clone  
- git status  
- git add  
- git commit  
- git push

## What was set up Week 4:

This week, the project was initialized and the core development environment was configured. A FastAPI application was created and successfully run using uvicorn. A virtual environment was set up to manage dependencies, and required Python packages such as FastAPI, uvicorn, and python-dotenv were installed. The project structure was organized, and Git was configured with a .gitignore file to prevent sensitive files like environment variables from being committed. An environment file was also created to securely store the Gemini API key. The local development server was verified to be working, and basic API endpoints were tested successfully.

## Purpose of rag_app.py

The rag_app.py file serves as the main entry point for the FastAPI application. Its current purpose is to initialize the web server, load environment variables from the .env file, and verify that the Gemini API key is properly configured. It also defines basic API endpoints used to confirm that the server is running correctly, including a root endpoint and a health check endpoint. At this stage, it does not implement any retrieval-augmented generation logic. Instead, it functions as a foundational scaffold that ensures the environment is correctly set up before building document processing, embedding generation, and Gemini-based response features in later stages.

## Week 5: /test-gemini

What /test-gemini does
Calls Gemini with one fixed prompt (no user input) and returns the answer as JSON: {"response": "..."}.

Where the Gemini call lives
rag_app.py → function test_gemini() (route: GET /test-gemini).

What I learned from the Gemini docs

Use the SDK to create a model/client, call generate_content with a prompt, and read the text from the response.
Model names must match what your API key supports (e.g. gemini-2.5-flash, not always gemini-1.5-flash).
Handle errors without exposing your API key.

## Week 6: Multi-step execution in `/test-gemini`

### Multi-step flow

The `/test-gemini` endpoint now runs two sequential Gemini calls inside `test_gemini()`:

1. **Step 1 (outline):** Ask Gemini to create a short bullet-point outline about what a large language model is. The result is stored in a variable and logged server-side only.
2. **Step 2 (expand):** Send a second prompt that includes the outline from step 1 and ask Gemini to write one full paragraph. Only this final answer is returned to the client as JSON.

### What each step does

- **Step 1** plans the answer structure (outline).
- **Step 2** uses that plan to produce the final, expanded response.

### Why the steps are separated

Splitting the work into two steps makes the output more controlled: the model first decides what to cover, then writes the full answer based on that plan. This same pattern (plan → execute, draft → refine) is used in real AI systems and will support later RAG and validation work.

### Challenges / open questions

- Model names can differ by API key, so a supported model must be chosen (e.g. `gemini-2.5-flash`).
- Multi-step calls take longer and use more API quota than a single call.
- Intermediate results are kept server-side for now; a future version could expose them for debugging or add a validation step.
