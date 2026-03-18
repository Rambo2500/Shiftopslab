# Cache bust: v2.1 (Fixing persistent SyntaxError in Cloud Build)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the intelligence subfolder
COPY ShiftOps-OS/core_intelligence/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all ShiftOps-OS contents to the root of /app
# This ensures platform_core, engines, and core_intelligence are available
COPY ShiftOps-OS/ .

# Set Python path to /app so modules can be found
ENV PYTHONPATH="/app:/app/core_intelligence"

EXPOSE 8080

# Run the API from the core-intelligence subfolder
# Use the PORT environment variable provided by Cloud Run
CMD ["sh", "-c", "uvicorn core_intelligence.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
