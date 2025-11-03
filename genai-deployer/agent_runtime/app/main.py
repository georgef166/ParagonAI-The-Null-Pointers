from fastapi import FastAPI, Body
from pydantic import BaseModel
import os
import requests

MODEL = os.getenv("MODEL", "OpenAI gpt-4o")
INSTRUCTION = os.getenv("INSTRUCTION", "You are a helpful assistant.")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="GenAI Agent Runtime")

class GenerateRequest(BaseModel):
    prompt: str

@app.get("/healthz")
def health():
    return {"ok": True, "model": MODEL}

@app.post("/generate")
def generate(req: GenerateRequest):
    # Minimal example using OpenAI Responses API if OPENAI_API_KEY set.
    # Otherwise, echo back a mock response.
    if OPENAI_API_KEY:
        try:
            # Simple demo call (adjust to your preferred OpenAI SDK / endpoint)
            # Here we just mock since internet isn't available in this environment.
            return {
                "model": MODEL,
                "instruction": INSTRUCTION,
                "prompt": req.prompt,
                "completion": f"[MOCKED] ({MODEL}) -> {req.prompt[:60]}..."
            }
        except Exception as e:
            return {"error": str(e)}
    else:
        # Mock response
        return {
            "model": MODEL,
            "instruction": INSTRUCTION,
            "prompt": req.prompt,
            "completion": f"[MOCKED] No API key. Echo: {req.prompt[:120]}"
        }
