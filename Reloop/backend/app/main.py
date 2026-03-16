"""
ReLoop Backend — FastAPI Main Entry Point
Wires all routers, CORS middleware, and creates DB tables on startup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api import auth, marketplace, chatbot, analytics, recommendations, notifications, requests, chat
from app.models.buy_request import BuyRequest  # Ensure model is registered for create_all


# --- Create all database tables ---
Base.metadata.create_all(bind=engine)

# --- FastAPI Application ---
app = FastAPI(
    title="ReLoop API",
    description="🔄 Circular Economy & Industrial Symbiosis Platform — Connecting waste generators with industries that reuse materials.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth.router)
app.include_router(marketplace.router)
app.include_router(chatbot.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(notifications.router)
app.include_router(requests.router)
app.include_router(chat.router)



@app.get("/", tags=["Root"])
def root():
    """Root endpoint — API health check."""
    return {
        "platform": "ReLoop",
        "tagline": "Circular Economy & Industrial Symbiosis Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "listings": "/listings",
            "recommendations": "/recommendations",
            "analytics": "/analytics",
            "chatbot": "/ws/chat",
        },
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint for Docker/monitoring."""
    return {"status": "healthy"}
