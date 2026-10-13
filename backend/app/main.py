from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes.analysis import router as analysis_router
from .api.routes.health import router as health_router


app = FastAPI(
    title="PULSO Backend",
    version="0.1.0",
)


app.include_router(
    health_router,
    prefix="/api",
)


app.include_router(
    analysis_router,
    prefix="/api",
)

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