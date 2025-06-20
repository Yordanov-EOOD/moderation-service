# Use Python 3.11 image (not slim) to avoid package installation issues
FROM python:3.11

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py
ENV PYTHONPATH=/app/src

# Copy requirements first for better caching
COPY moderation-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY moderation-service/src/ ./src/
COPY moderation-service/.env.example .env

# Create models directory for ML model cache
RUN mkdir -p ./models

# Add src directory to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application with longer timeout for ML model loading
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--chdir", "/app/src", "app:app"]
