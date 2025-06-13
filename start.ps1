# Moderation Service Startup Script for Windows

Write-Host "🚀 Starting Moderation Service..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Copying environment configuration..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please review and update .env file with your settings" -ForegroundColor Cyan
}

# Load environment variables
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Pre-download ML model (optional)
$useMLModel = $env:USE_ML_MODEL
if ($useMLModel -eq $null) { $useMLModel = "true" }

if ($useMLModel.ToLower() -eq "true") {
    Write-Host "🤖 Pre-loading ML model (this may take a few minutes)..." -ForegroundColor Yellow
    $modelScript = @"
from src.services.toxicity_detector import ToxicityDetector
print('Initializing detector...')
detector = ToxicityDetector(use_ml_model=True)
print('Model loaded successfully!')
"@
    
    try {
        python -c $modelScript
        Write-Host "✅ ML model loaded successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ ML model loading failed, will fall back to rule-based detection" -ForegroundColor Yellow
    }
}

# Set Flask environment variables
$env:FLASK_APP = "src/app.py"
$env:FLASK_ENV = if ($env:FLASK_ENV) { $env:FLASK_ENV } else { "production" }
$port = if ($env:PORT) { $env:PORT } else { "5000" }

# Start the service
Write-Host "🌟 Starting Moderation Service on port $port..." -ForegroundColor Green

# Run with gunicorn for production or flask for development
if ($env:FLASK_ENV -eq "development") {
    Write-Host "🔧 Running in development mode..." -ForegroundColor Cyan
    flask run --host=0.0.0.0 --port=$port
}
else {
    Write-Host "🏭 Running in production mode..." -ForegroundColor Cyan
    gunicorn --bind "0.0.0.0:$port" --workers 2 --timeout 120 src.app:app
}
