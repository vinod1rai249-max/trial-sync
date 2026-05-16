# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 and database connectivity
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run uses $PORT environment variable, default 8080)
EXPOSE 8080

# Run the application with Uvicorn
# We use the $PORT env var provided by Cloud Run
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
