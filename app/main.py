from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- NEW IMPORT
from influencer_agent.app.core.config import settings
from influencer_agent.app.db.session import engine
from influencer_agent.app.db.base import Base
from influencer_agent.app.models import *
from influencer_agent.app.api import routes_instagram, routes_auth, routes_analytics
from influencer_agent.worker.celery_app import celery_app

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

# --- CORS FIX: Allow the local HTML file (origin 'null') to talk to the API ---
# The 'null' origin is mandatory for file:// access
origins = [
    "http://127.0.0.1:8000",
    "http://localhost",
    "null", 
    "*" # We add '*' temporarily for full flexibility during development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)
# ----------------------------------------------------------------------------


# Include Routers
app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(routes_instagram.router, prefix="/api/v1/instagram", tags=["instagram"])
app.include_router(routes_analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
def root():
    return {
        "message": "Influencer Agent is running",
        "database": "Connected",
        "mode": "Autonomous",
        "docs_url": "/docs"
    }
