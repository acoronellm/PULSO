from fastapi import FastAPI


app = FastAPI(
    title="PULSO ML Service",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ml-service",
        "model_version": "v1",
    }