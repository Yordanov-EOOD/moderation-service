# Moderation Service API Documentation

## Overview
The Moderation Service provides endpoints to check if social media posts (called "yeets") contain toxic content. It uses a custom-trained machine learning model specifically designed for toxicity detection, with fallback to rule-based approaches when needed.

### Detection Methods
1. **ML-Based Detection (Primary)**: Uses the custom-trained `toxicity-model-final` model optimized for yeet content
2. **Rule-Based Detection (Fallback)**: Uses pattern matching and keyword detection when ML model is unavailable

### Features
- Real-time toxicity detection for individual posts
- Batch processing for multiple posts
- Configurable toxicity thresholds
- Multiple toxicity category classification
- High accuracy with confidence scoring
- Custom-trained model for better domain-specific performance

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, no authentication is required for this service. In production, you should implement proper authentication and authorization.

## Endpoints

### Health Check
Check if the service is running properly.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "moderation-service",
  "version": "1.0.0"
}
```

### Check Single Yeet Toxicity
Check if a single yeet contains toxic content.

**Endpoint:** `POST /api/moderation/check`

**Request Body:**
```json
{
  "content": "The text content to check for toxicity",
  "yeet_id": "optional_yeet_identifier",
  "user_id": "optional_user_identifier"
}
```

**Required Fields:**
- `content` (string): The text content to analyze (max 10,000 characters)

**Optional Fields:**
- `yeet_id` (string): Identifier for the yeet being checked
- `user_id` (string): Identifier for the user who posted the content

**Response:**
```json
{
  "is_toxic": false,
  "toxicity_score": 0.234,
  "confidence": 0.789,
  "categories": ["profanity", "harassment"],
  "content_length": 45,
  "yeet_id": "yeet_123",
  "user_id": "user_456",  "timestamp": "2025-06-07T10:30:00.000Z",
  "detector_version": "2.0.0-ml",
  "model_used": "unitary/toxic-bert"
}
```

**Response Fields:**
- `is_toxic` (boolean): Whether the content is considered toxic
- `toxicity_score` (float): Toxicity score from 0.0 to 1.0
- `confidence` (float): Confidence in the prediction from 0.0 to 1.0
- `categories` (array): Array of toxicity categories detected
- `content_length` (number): Length of the analyzed content
- `yeet_id` (string): Echoed yeet ID if provided
- `user_id` (string): Echoed user ID if provided
- `timestamp` (string): ISO timestamp of the analysis
- `detector_version` (string): Version of the detection algorithm

### Batch Toxicity Check
Check toxicity for multiple yeets at once.

**Endpoint:** `POST /api/moderation/batch`

**Request Body:**
```json
{
  "yeets": [
    {
      "content": "First yeet content",
      "yeet_id": "yeet_1",
      "user_id": "user_1"
    },
    {
      "content": "Second yeet content",
      "yeet_id": "yeet_2",
      "user_id": "user_2"
    }
  ]
}
```

**Limits:**
- Maximum 100 yeets per batch request
- Each yeet follows the same validation rules as single check

**Response:**
```json
{
  "results": [
    {
      "is_toxic": false,
      "toxicity_score": 0.123,
      "confidence": 0.856,
      "categories": [],
      "content_length": 18,
      "yeet_id": "yeet_1",
      "user_id": "user_1",
      "timestamp": "2025-06-07T10:30:00.000Z",
      "detector_version": "1.0.0"
    },
    {
      "is_toxic": true,
      "toxicity_score": 0.887,
      "confidence": 0.923,
      "categories": ["hate_speech", "harassment"],
      "content_length": 22,
      "yeet_id": "yeet_2",
      "user_id": "user_2",
      "timestamp": "2025-06-07T10:30:00.001Z",
      "detector_version": "1.0.0"
    }
  ],
  "total_processed": 2
}
```

### Get Detector Information
Get information about the current toxicity detection method and model.

**Endpoint:** `GET /api/moderation/info`

**Response:**
```json
{
  "detector_type": "ml_model",
  "version": "2.0.0",
  "model_name": "unitary/toxic-bert",
  "framework": "transformers",
  "description": "ML-based toxicity detector using pre-trained BERT model"
}
```

**Response Fields:**
- `detector_type` (string): Type of detector ("ml_model" or "rule_based")
- `version` (string): Version of the detection system
- `model_name` (string): Name of the ML model (if using ML detection)
- `framework` (string): ML framework used (if applicable)
- `description` (string): Human-readable description of the detector

## Toxicity Categories

The service can detect the following types of toxic content:

### ML Model Categories
- **general_toxicity**: Overall toxic content detected by the ML model
- **profanity**: Explicit language and swear words
- **hate_speech**: Content targeting individuals or groups based on protected characteristics
- **harassment**: Bullying, threats, or targeted harassment
- **threat**: Direct threats or violent language

### Rule-Based Categories (Fallback)
- **profanity**: Explicit language and swear words
- **hate_speech**: Content targeting individuals or groups based on protected characteristics
- **harassment**: Bullying, threats, or targeted harassment
- **toxic_behavior**: Spam, trolling, or other disruptive behavior

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required field: content"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Failed to check content toxicity"
}
```

## Rate Limiting
- Default: 100 requests per minute per IP
- Batch requests count as 1 request regardless of batch size

## Content Validation
- Content must be a non-empty string
- Maximum content length: 10,000 characters
- Content is automatically sanitized to remove potentially harmful characters
- IDs must be alphanumeric with hyphens/underscores, max 50 characters

## Example Usage

### cURL Example
```bash
curl -X POST http://localhost:5000/api/moderation/check \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test message",
    "yeet_id": "test_123",
    "user_id": "user_456"
  }'
```

### JavaScript Example
```javascript
const response = await fetch('http://localhost:5000/api/moderation/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: 'This is a test message',
    yeet_id: 'test_123',
    user_id: 'user_456'
  })
});

const result = await response.json();
console.log('Is toxic:', result.is_toxic);
```

## Deployment

### Using Docker
```bash
# Build the image
docker build -t moderation-service .

# Run the container
docker run -p 5000:5000 moderation-service
```

### Environment Variables
Key configuration options (see `.env.example` for full list):

#### Model Configuration
- `MODEL_NAME=toxicity-model-final` - Name/path of the custom toxicity detection model
- `MODEL_CACHE_DIR=./models` - Directory to cache downloaded models
- `USE_GPU=false` - Whether to use GPU acceleration (requires CUDA)

#### Service Configuration  
- `USE_ML_MODEL=true` - Enable ML-based detection (falls back to rule-based if false)
- `TOXICITY_THRESHOLD=0.5` - Minimum score to consider content toxic
- `CONFIDENCE_THRESHOLD=0.3` - Minimum confidence for ML predictions

#### Performance Settings
- `BATCH_SIZE_LIMIT=100` - Maximum number of posts in batch requests
- `CONTENT_LENGTH_LIMIT=10000` - Maximum character length per post
- `RATE_LIMIT_PER_MINUTE=100` - API rate limiting

## Custom Model Setup

This service uses a custom-trained model `toxicity-model-final` for optimal performance on yeet content. 

### Model Requirements
1. The model should be compatible with Hugging Face Transformers
2. Must support text classification for toxicity detection
3. Should be placed in the `./models` directory or accessible via the `MODEL_NAME` path

### Testing Your Custom Model
Run the test script to verify your model is working:
```bash
python test_custom_model.py
```

This will test both the custom model and fallback mechanisms.
