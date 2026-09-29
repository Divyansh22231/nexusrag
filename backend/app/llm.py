import httpx
import json
from typing import AsyncGenerator
from app.config import settings
from app.prompts import build_rag_prompt

async def generate_rag_response(question: str, context_chunks: list) -> AsyncGenerator[str, None]:
    if not settings.GEMINI_API_KEY:
        yield "data: {\"error\": \"Gemini API key is not configured.\"}\n\n"
        return

    if not context_chunks:
        yield "data: {\"token\": \"I couldn't find that information in the uploaded document.\"}\n\n"
        yield "data: {\"done\": true}\n\n"
        return

    prompt = build_rag_prompt(question, context_chunks)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:streamGenerateContent?alt=sse"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.GEMINI_API_KEY
    }
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code == 401 or response.status_code == 403:
                    yield "data: {\"error\": \"Authentication failed with Gemini API.\"}\n\n"
                    return
                elif response.status_code == 404:
                    yield "data: {\"error\": \"Invalid Gemini model specified.\"}\n\n"
                    return
                elif response.status_code == 429:
                    yield "data: {\"error\": \"Gemini rate limit or quota exceeded. Please try again later.\"}\n\n"
                    return
                elif response.status_code != 200:
                    yield f"data: {{\"error\": \"Gemini API error: {response.status_code}\"}}\n\n"
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            continue
                        try:
                            data_json = json.loads(data_str)
                            if "candidates" in data_json and len(data_json["candidates"]) > 0:
                                candidate = data_json["candidates"][0]
                                if "content" in candidate and "parts" in candidate["content"]:
                                    part = candidate["content"]["parts"][0]
                                    if "text" in part:
                                        token = part["text"]
                                        clean_token = json.dumps({"token": token})
                                        yield f"data: {clean_token}\n\n"
                        except json.JSONDecodeError:
                            pass
        yield "data: {\"done\": true}\n\n"
    except Exception as e:
        yield "data: {\"error\": \"Network or stream error occurred.\"}\n\n"
