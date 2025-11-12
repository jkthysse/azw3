FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY src/python/ ./src/python/

# Install Python package
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AZW3_STACK=python

# Expose port (if needed for API)
EXPOSE 8080

# Run pipeline
CMD ["python", "-m", "azw3.cli"]

