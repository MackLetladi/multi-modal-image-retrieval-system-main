import json

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import uvicorn
import os
import logging
import time

from backend.src.models.retrieval_model import MultiModalRetrieval
from backend.src.data.data_loader import ImageDataset
from backend.src.config import (
    MODEL_NAME,
    DEVICE,
    TOP_K,
    API_HOST,
    API_PORT,
    CORS_ORIGINS,
    DATA_DIR
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Development CSP - more permissive for development tools
        if os.getenv("ENVIRONMENT", "development") == "development":
            csp = (
                "default-src 'self'; "
                "connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* http://127.0.0.1:*; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob: http://localhost:* http://127.0.0.1:*; "
                "font-src 'self' data:; "
                "worker-src 'self' blob:;"
            )
        else:
            # Production CSP - more restrictive
            csp = (
                "default-src 'self'; "
                "connect-src 'self' wss://*; "  # Using wss (secure WebSocket) in production
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "font-src 'self' data:; "
                "worker-src 'self' blob:;"
            )

        # Set security headers
        response.headers["Content-Security-Policy"] = csp
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


# Initialize FastAPI app
app = FastAPI(
    title="Image Retrieval API",
    description="API for multi-modal image retrieval using CLIP",
    version="1.0.0"
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this appropriately in production
)

# Initialize the retrieval model
retrieval_model = None
dataset = None


# Rate limiting
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []

    def is_allowed(self) -> bool:
        now = time.time()
        minute_ago = now - 60

        # Remove requests older than 1 minute
        self.requests = [req for req in self.requests if req > minute_ago]

        if len(self.requests) >= self.requests_per_minute:
            return False

        self.requests.append(now)
        return True


rate_limiter = RateLimiter()


class SearchQuery(BaseModel):
    """Model for search query requests."""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=TOP_K, ge=1, le=20)


class SearchResult(BaseModel):
    """Model for search results."""
    url: str
    score: float = Field(..., ge=0, le=1)


@app.on_event("startup")
async def startup_event():
    """Initialize the model and dataset on startup."""
    global retrieval_model, dataset

    try:
        logger.info("Starting up the server...")

        # Initialize the model
        retrieval_model = MultiModalRetrieval(MODEL_NAME, DEVICE)

        # Mount static files directory for serving images
        static_dir = DATA_DIR
        if not static_dir.exists():
            raise ValueError(f"Data directory not found: {static_dir}")

        # Create StaticFiles instance with proper configuration
        static_files = StaticFiles(directory=str(static_dir), check_dir=True, html=True)
        app.mount("/images", static_files, name="images")

        # Load the dataset with no image limit
        dataset = ImageDataset(str(static_dir), max_images=None)  # Allow loading all available images

        # Build the index
        retrieval_model.build_index(dataset)

        logger.info("Server startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to add processing time header and handle rate limiting."""
    # Check rate limit
    if not rate_limiter.is_allowed():
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not retrieval_model or not dataset:
        raise HTTPException(
            status_code=503,
            detail="Service is starting up or unavailable"
        )
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "device": DEVICE,
        "dataset_size": len(dataset) if dataset else 0
    }


@app.post("/search", response_model=List[SearchResult])
async def search_images(query: SearchQuery):
    """
    Search for images matching the query text.
    
    Args:
        query (SearchQuery): Search query parameters
        
    Returns:
        List[SearchResult]: List of search results
    """
    try:
        if not retrieval_model:
            raise HTTPException(
                status_code=503,
                detail="Model not initialized"
            )

        logger.info(f" Processing search query: {query.query}")
        results = retrieval_model.search(query.query, query.top_k)

        return [
            SearchResult(url=url, score=score)
            for url, score in results
        ]

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(time.time())  # Simple way to generate unique client ID
    try:
        await manager.connect(websocket, client_id)
        while True:
            try:
                data = await websocket.receive_text()
                # Process the received data
                response_data = {"status": "received", "message": data}
                await manager.send_message(json.dumps(response_data), client_id)
            except WebSocketDisconnect:
                manager.disconnect(client_id)
                break
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        manager.disconnect(client_id)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
