# Use official Python runtime as base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vnstat \
        curl \
        procps \
        net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create vnstat user and group
RUN groupadd -r vnstat && useradd -r -g vnstat vnstat

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY dashboard.py .
COPY vnstat_parser.py .
COPY config.py .
COPY templates/ templates/

# Create logs directory
RUN mkdir -p logs \
    && chown -R vnstat:vnstat /app

# Copy entrypoint script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Switch to non-root user
USER vnstat

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["python", "dashboard.py"] 