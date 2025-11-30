# syntax=docker/dockerfile:1

# Stage 1: build the Next.js frontend so the backend can serve the static output.
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: install backend runtime dependencies and assemble the final image.
FROM python:3.10-slim AS runtime

# Ensure deterministic runtime behaviour and install system packages once.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Install OS dependencies required by PyMuPDF/Tesseract.
RUN apt-get update \ 
    && apt-get install -y --no-install-recommends tesseract-ocr libgl1-mesa-glx \ 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip \ 
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source code.
COPY . .

# Bring in the pre-built frontend assets from the builder stage.
COPY --from=frontend-builder /app/frontend/out /app/frontend/out

EXPOSE 8080

# Cloud Run injects PORT; default to 8080 for local runs as well.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
