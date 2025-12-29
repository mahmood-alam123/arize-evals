"""
FastAPI server for the Quality Dashboard.
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api import runs
from .database import get_database


def create_app(db_path: str = "eval_results.db") -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Company Eval Dashboard",
        description="Quality Dashboard for tracking LLM evaluation results",
        version="1.0.0",
    )

    # CORS middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database
    get_database(db_path)

    # Include API routes
    app.include_router(runs.router)

    # Health check endpoint
    @app.get("/api/health")
    def health_check():
        return {"status": "healthy", "database": db_path}

    # Serve frontend static files
    frontend_dist = Path(__file__).parent / "frontend" / "dist"
    if frontend_dist.exists():
        # Serve static assets
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

        # Serve index.html for all non-API routes (SPA routing)
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            # Don't serve index.html for API routes
            if full_path.startswith("api/"):
                return {"error": "Not found"}

            index_file = frontend_dist / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            return {"error": "Frontend not built. Run the build script first."}

    else:
        @app.get("/")
        def no_frontend():
            return {
                "message": "Dashboard API is running",
                "note": "Frontend not built. See /api/health for API status.",
                "docs": "/docs",
            }

    return app


def main(
    host: str = "0.0.0.0",
    port: int = 8080,
    db_path: str = "eval_results.db",
    reload: bool = False,
):
    """Run the dashboard server.

    Args:
        host: Host to bind to.
        port: Port to listen on.
        db_path: Path to SQLite database.
        reload: Enable auto-reload for development.
    """
    import uvicorn

    # Set database path via environment for the app factory
    os.environ["EVAL_DASHBOARD_DB"] = db_path

    uvicorn.run(
        "company_eval_framework.dashboard.server:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
