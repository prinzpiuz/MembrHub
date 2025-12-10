from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.accounts.router import router as accounts_router
from src.auth.router import router as auth_router
from src.communities.router import router as communities_router
from src.core.config import settings
from src.exceptions import configure_exception_handlers
from src.membership.router import router as membership_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
        if settings.is_development
        else None,
        docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.is_development else None,
        redoc_url=f"{settings.API_V1_PREFIX}/redoc"
        if settings.is_development
        else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    configure_exception_handlers(app)

    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(accounts_router, prefix=settings.API_V1_PREFIX)
    app.include_router(communities_router, prefix=settings.API_V1_PREFIX)
    app.include_router(membership_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION}

    return app


app = create_app()
