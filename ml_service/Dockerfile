FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ml_service/requirements.txt /app/ml_service/requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir \
       -r /app/ml_service/requirements.txt

COPY ml_service /app/ml_service
COPY models/pulso/v1/pulso_xgboost.joblib /app/artifacts/final/model/pulso_xgboost.joblib
EXPOSE 8001

CMD ["python","-m","uvicorn","ml_service.app.main:app","--host","0.0.0.0","--port","8001"]
