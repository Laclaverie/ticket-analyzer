from contextlib import asynccontextmanager

from fastapi import FastAPI

from api_service.database import create_all_tables
from api_service.config import Settings
from api_service.routers import health, receipts, jobs, analytics


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Tables are created by Alembic migrations in production.
        # In development, create_all_tables ensures the DB is ready without running Alembic.
        create_all_tables(resolved_settings.database_url)
        yield

    app = FastAPI(
        title="Ticket Analyzer API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.include_router(health.router)
    app.include_router(receipts.router)
    app.include_router(jobs.router)
    app.include_router(analytics.router)
    return app


app = create_app()
