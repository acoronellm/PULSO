from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .interfaces.http.errors import register_exception_handlers
from .interfaces.http.routes.analysis import router as analysis_router
from .interfaces.http.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="PULSO Backend",
        version="0.1.0",
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(analysis_router, prefix="/api")
    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


# Punto de entrada usado por Uvicorn: backend.app.main:app
app = create_app()
