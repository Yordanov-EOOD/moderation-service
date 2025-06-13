#!/bin/bash

# Moderation Service Startup Script

echo "🚀 Starting Moderation Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Copying environment configuration..."
    cp .env.example .env
    echo "📝 Please review and update .env file with your settings"
fi

# Pre-download ML model (optional)
if [ "${USE_ML_MODEL:-true}" = "true" ]; then
    echo "🤖 Pre-loading ML model (this may take a few minutes)..."
    python -c "
from src.services.toxicity_detector import ToxicityDetector
print('Initializing detector...')
detector = ToxicityDetector(use_ml_model=True)
print('Model loaded successfully!')
" || echo "⚠️ ML model loading failed, will fall back to rule-based detection"
fi

# Start the service
echo "🌟 Starting Moderation Service on port ${PORT:-5000}..."
export FLASK_APP=src/app.py
export FLASK_ENV=${FLASK_ENV:-production}

# Run with gunicorn for production or flask for development
if [ "${FLASK_ENV}" = "development" ]; then
    flask run --host=0.0.0.0 --port=${PORT:-5000}
else
    gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 src.app:app
fi
