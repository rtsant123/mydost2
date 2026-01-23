FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY backend/requirements.txt .

# Install dependencies (including requests for health check)
RUN pip install --no-cache-dir fastapi uvicorn requests

# Install all other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/

# Expose port
EXPOSE ${PORT:-8000}

# Start FastAPI app
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
