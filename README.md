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
