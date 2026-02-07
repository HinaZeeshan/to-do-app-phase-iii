# Use Python 3.11 slim image for smaller footprint
FROM python:3.11-slim

# Set working directory to /app as expected by Hugging Face Spaces
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir ".[dev]"

# Copy application code to /app directory
COPY . .

# Expose port 7860 as required by Hugging Face Spaces
EXPOSE 7860

# Run the application with proper host and port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]