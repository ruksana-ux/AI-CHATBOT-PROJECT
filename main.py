"""FastAPI Backend for AI Customer Support Assistant with Media Support."""
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from assistant import CustomerSupportAssistant

app = FastAPI(
    title="AI Customer Support Assistant API",
    description="Real-time REST API for AI Customer Support handling text queries, FAQs, order verification, and media attachments (images/videos).",
    version="1.0.0"
)

bot = CustomerSupportAssistant()


class QueryRequest(BaseModel):
    message: str
    media_urls: Optional[List[str]] = None  # List of image/video URLs


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AI Customer Support Assistant API",
        "docs_url": "/docs"
    }


@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    """
    Handle customer chat messages and optional media attachments.
    """
    try:
        # Pass media_urls from the request to your assistant logic
        response = bot.respond(request.message, media_urls=request.media_urls)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

