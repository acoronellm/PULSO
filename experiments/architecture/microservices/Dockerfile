FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
COPY ml_service/requirements.txt /app/ml_service/requirements.txt

RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r /app/backend/requirements.txt && python -m pip install --no-cache-dir -r /app/ml_service/requirements.txt

COPY backend /app/backend
COPY ml_service /app/ml_service
COPY experiments /app/experiments