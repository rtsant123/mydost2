FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir fastapi uvicorn anthropic

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || echo "Some deps failed to install - will continue"

# Copy app
COPY backend/ /app/

EXPOSE 8000

# Start with explicit command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "65"]
