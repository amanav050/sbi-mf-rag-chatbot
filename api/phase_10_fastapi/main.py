import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

from .models import ChatRequest, ChatResponse
from query.phase_9_refusal.refusal_handler import is_advisory, get_refusal_response
from query.phase_9_refusal.citation_formatter import format_response
from query.phase_7_retriever.retriever import retrieve
from query.phase_8_llm.llm_handler import generate_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="SBI MF RAG Chatbot", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Mount UI static files at /ui path to avoid conflicts with API endpoints
ui_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ui", "phase_11_ui")
if os.path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path, html=True), name="ui")
    logger.info(f"UI mounted from: {ui_path} at /ui")
else:
    logger.warning(f"UI directory not found: {ui_path}")

# Redirect root to UI
@app.get("/")
async def redirect_to_ui():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/ui")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    query = body.query.strip()
    session_id = body.session_id

    if is_advisory(query):
        refusal = get_refusal_response()
        return ChatResponse(
            answer=refusal["answer"],
            source_url=refusal["source_url"],
            scraped_date=refusal["scraped_date"],
            session_id=session_id,
            is_refusal=True
        )

    chunks = retrieve(query)

    if not chunks:
        return ChatResponse(
            answer="This information is not available in current sources. Please visit https://www.sbimf.com for more details.",
            source_url="https://www.sbimf.com",
            scraped_date="N/A",
            session_id=session_id
        )

    llm_result = generate_response(query, chunks)
    formatted_answer = format_response(
        llm_result["answer"],
        llm_result["source_url"],
        llm_result["scraped_date"]
    )

    return ChatResponse(
        answer=formatted_answer,
        source_url=llm_result["source_url"],
        scraped_date=llm_result["scraped_date"],
        session_id=session_id
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.phase_10_fastapi.main:app", host="0.0.0.0", port=8000, reload=True)
