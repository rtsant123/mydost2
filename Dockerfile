FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir fastapi uvicorn

RUN pip install --no-cache-dir -r requirements.txt || true

COPY backend/ /app/

EXPOSE 8000

CMD exec uvicorn main:app --host 0.0.0.0 --port 8000
