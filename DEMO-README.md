# Moderation Service Demo Scripts

This directory contains demo scripts to showcase the AI-powered toxicity detection capabilities of the moderation service.

## ⚠️ Content Warning

**The demo scripts include examples of toxic content for testing purposes.** These examples are intentionally included to demonstrate the full range of the moderation service's capabilities, from clean content to severely toxic material. The toxic examples are clearly labeled and used solely for educational and testing purposes.

## Available Scripts

### 1. PowerShell Demo Script (`demo-moderation.ps1`)
A Windows PowerShell script with colorful output and interactive features.

**Usage:**
```powershell
# Basic demo with automated tests
.\demo-moderation.ps1

# Interactive mode
.\demo-moderation.ps1 -Interactive

# Custom service URL
.\demo-moderation.ps1 -ServiceUrl "http://localhost:5000"

# Skip automated tests
.\demo-moderation.ps1 -RunTests:$false -Interactive
```

### 2. Python Demo Script (`demo_moderation.py`)
A cross-platform Python script with rich features and statistics.

**Usage:**
```bash
# Basic demo with automated tests
python demo_moderation.py

# Interactive mode
python demo_moderation.py --interactive

# Custom service URL
python demo_moderation.py --url "http://localhost:5000"

# Skip automated tests
python demo_moderation.py --no-tests --interactive
```

**Requirements:**
```bash
pip install requests
```

## Features

### 🏥 Health Check
- Verifies service availability
- Shows service information
- Displays model details

### 🧪 Automated Testing
- Tests various content types
- Demonstrates different toxicity levels
- Shows response formatting

### 📦 Batch Testing
- Tests multiple contents simultaneously
- Demonstrates batch API usage
- Performance comparison

### 📈 Statistics
- Summary of test results
- Toxicity distribution analysis
- Confidence score averages

### 🎮 Interactive Mode
- Real-time content testing
- User input validation
- Continuous analysis capability

## Sample Output

```
🧪 Testing: Positive content
Content: "What a beautiful day! I love this sunshine."

Status: ✅ CLEAN
Toxicity Score: 0.123 / 1.0
Confidence: 0.877
Model Used: unitary/toxic-bert
Categories: None detected
Content Length: 42 characters
Timestamp: 2025-06-10T10:32:15.123456
```

## Demo Test Cases

The scripts include various test cases:

1. **Positive Content**: Happy, uplifting messages
2. **Neutral Content**: Factual statements, technical discussions
3. **Negative (Non-toxic)**: Complaints without toxicity
4. **Respectful Disagreement**: Polite opposing views
5. **Technical Content**: Programming, science discussions

## Service Requirements

Before running the demo scripts, ensure:

1. **Service Running**: The moderation service is running on the specified URL
2. **Docker**: If using Docker, the service container is up
3. **Network Access**: The demo script can reach the service endpoint

**Check if service is running:**
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the moderation service is running
   - Check the correct port (default: 5000)
   - Verify Docker container status

2. **Timeout Errors**
   - ML model loading can take time on first request
   - Increase timeout in script if needed
   - Check service logs for issues

3. **Import Errors (Python)**
   - Install required packages: `pip install requests`
   - Use Python 3.6+ for best compatibility

### Service Status Commands

```bash
# Check Docker containers
docker ps | grep moderation

# Check service logs
docker-compose logs moderation-service

# Test service directly
curl http://localhost:5000/health
```

## Customization

### Adding Custom Test Cases

Edit the test cases in either script:

**PowerShell:**
```powershell
$testCases = @(
    @{ content = "Your custom message"; description = "Your description" }
)
```

**Python:**
```python
test_cases = [
    {"content": "Your custom message", "description": "Your description"}
]
```

### Changing Service URL

Both scripts support custom URLs:
- PowerShell: `-ServiceUrl "http://your-service:port"`
- Python: `--url "http://your-service:port"`

### Modifying Output Colors

Edit the color definitions at the top of each script to customize the appearance.

## API Endpoints Demonstrated

1. `GET /health` - Service health check
2. `GET /api/moderation/info` - Service information
3. `POST /api/moderation/check` - Single content analysis
4. `POST /api/moderation/batch` - Batch content analysis

## Performance Notes

- **First Request**: May take longer due to ML model initialization
- **Subsequent Requests**: Much faster with cached model
- **Batch Processing**: More efficient for multiple contents
- **Network Latency**: Consider if service is remote

## Security Considerations

- Demo scripts are for **testing purposes only**
- Do not include sensitive content in tests
- Use appropriate authentication in production
- Monitor API usage and rate limits
