"""
Company Eval Dashboard - FastAPI Backend

A web application for viewing LLM evaluation results.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import create_tables
from .api import runs
from .seed import seed_demo_data

# Create FastAPI app
app = FastAPI(
    title="Company Eval Dashboard",
    description="Quality Dashboard for LLM Evaluation Results",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(runs.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed demo data on startup."""
    create_tables()
    # Seed demo data if SEED_DEMO_DATA env var is set
    if os.environ.get("SEED_DEMO_DATA", "true").lower() == "true":
        seed_demo_data()


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve frontend static files
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for all non-API routes."""
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend not built"}
else:
    @app.get("/")
    def root():
        """Root endpoint when frontend not built."""
        return {
            "message": "Company Eval Dashboard API",
            "docs": "/docs",
            "note": "Frontend not built. Run 'npm run build' in frontend/",
        }
