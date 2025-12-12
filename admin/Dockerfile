# syntax=docker/dockerfile:1

# ------------------------------
# Stage 1: Builder
# ------------------------------
ARG PYTHON_VERSION=3.12.9
FROM python:${PYTHON_VERSION}-slim as builder

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Unbuffer stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# ------------------------------
# Stage 2: Final Runtime
# ------------------------------
FROM python:${PYTHON_VERSION}-slim

# Copy Python environment from builder
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy only the app and installed dependencies
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Expose the application port
EXPOSE 8000

# Run the application
CMD uvicorn 'admin:app' --host=0.0.0.0 --port=8000