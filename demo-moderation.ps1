# Moderation Service Demo Script
# This script demonstrates the toxicity detection capabilities of the moderation service

param(
    [string]$ServiceUrl = "http://localhost:5000",
    [switch]$Interactive = $false,
    [switch]$RunTests = $true
)

# Colors for output
$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
    Toxic = "Red"
    Clean = "Green"
    Neutral = "Yellow"
}

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorText "=" * 60 -Color $Colors.Header
    Write-ColorText " $Title" -Color $Colors.Header
    Write-ColorText "=" * 60 -Color $Colors.Header
    Write-Host ""
}

function Format-ToxicityResult {
    param($Result)
    
    if ($Result.is_toxic) {
        $statusColor = $Colors.Toxic
        $status = "🚨 TOXIC"
    } else {
        $statusColor = $Colors.Clean
        $status = "✅ CLEAN"
    }
    
    Write-ColorText "Status: $status" -Color $statusColor
    Write-ColorText "Toxicity Score: $($Result.toxicity_score) / 1.0" -Color $Colors.Info
    Write-ColorText "Confidence: $($Result.confidence)" -Color $Colors.Info
    Write-ColorText "Model Used: $($Result.model_used)" -Color $Colors.Info
    
    if ($Result.categories -and $Result.categories.Count -gt 0) {
        Write-ColorText "Categories: $($Result.categories -join ', ')" -Color $Colors.Warning
    } else {
        Write-ColorText "Categories: None detected" -Color $Colors.Info
    }
    
    Write-ColorText "Content Length: $($Result.content_length) characters" -Color $Colors.Info
    Write-ColorText "Timestamp: $($Result.timestamp)" -Color $Colors.Info
    Write-Host ""
}

function Test-ServiceHealth {
    Write-Header "🏥 HEALTH CHECK"
    
    try {
        $response = Invoke-RestMethod -Uri "$ServiceUrl/health" -Method GET
        Write-ColorText "✅ Service is healthy!" -Color $Colors.Success
        Write-ColorText "Service: $($response.service)" -Color $Colors.Info
        Write-ColorText "Version: $($response.version)" -Color $Colors.Info
        Write-ColorText "Detector Type: $($response.detector.detector_type)" -Color $Colors.Info
        Write-ColorText "Model: $($response.detector.model_name)" -Color $Colors.Info
        return $true
    }
    catch {
        Write-ColorText "❌ Service health check failed: $($_.Exception.Message)" -Color $Colors.Error
        return $false
    }
}

function Test-SingleContent {
    param(
        [string]$Content,
        [string]$Description = ""
    )
    
    if ($Description) {
        Write-ColorText "🧪 Testing: $Description" -Color $Colors.Header
    }
    Write-ColorText "Content: `"$Content`"" -Color $Colors.Info
    Write-Host ""
    
    try {
        $body = @{
            content = $Content
            yeet_id = "demo-$(Get-Random)"
            user_id = "demo-user"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$ServiceUrl/api/moderation/check" -Method POST -Body $body -ContentType "application/json"
        Format-ToxicityResult $response
    }
    catch {
        Write-ColorText "❌ Error testing content: $($_.Exception.Message)" -Color $Colors.Error
        Write-Host ""
    }
}

function Test-BatchContent {
    Write-Header "📦 BATCH TESTING"
      $testMessages = @(
        @{ content = "I love spending time with my friends!"; description = "✅ Positive message" },
        @{ content = "This weather is absolutely terrible today"; description = "😐 Negative but not toxic" },
        @{ content = "You're such an amazing person"; description = "✅ Compliment" },
        @{ content = "That's really annoying and frustrating"; description = "⚠️ Mild negativity" },
        @{ content = "You're being stupid about this"; description = "🚨 Insulting language" }
    )
    
    $yeets = @()
    foreach ($msg in $testMessages) {
        $yeets += @{
            content = $msg.content
            yeet_id = "batch-$(Get-Random)"
            user_id = "demo-user"
        }
    }
    
    try {
        $body = @{ yeets = $yeets } | ConvertTo-Json -Depth 3
        $response = Invoke-RestMethod -Uri "$ServiceUrl/api/moderation/batch" -Method POST -Body $body -ContentType "application/json"
        
        Write-ColorText "📊 Batch Results (Total: $($response.total_processed))" -Color $Colors.Header
        Write-Host ""
        
        for ($i = 0; $i -lt $response.results.Count; $i++) {
            Write-ColorText "[$($i + 1)] $($testMessages[$i].description)" -Color $Colors.Info
            Write-ColorText "Content: `"$($testMessages[$i].content)`"" -Color $Colors.Info
            Format-ToxicityResult $response.results[$i]
        }
    }
    catch {
        Write-ColorText "❌ Error in batch testing: $($_.Exception.Message)" -Color $Colors.Error
    }
}

function Run-DemoTests {
    Write-Header "🚀 MODERATION SERVICE DEMO"
    
    # Test service health
    if (-not (Test-ServiceHealth)) {
        Write-ColorText "Cannot proceed without healthy service. Please start the moderation service." -Color $Colors.Error
        return
    }
    
    Write-Header "🧪 SINGLE CONTENT TESTS"
      # Test cases with various content types (from clean to toxic)
    $testCases = @(
        @{ content = "What a beautiful day! I love this sunshine."; description = "✅ Positive content" },
        @{ content = "I'm having a challenging day, but I'll get through it."; description = "😐 Neutral/slightly negative" },
        @{ content = "This is just a normal comment about technology."; description = "😐 Neutral technical content" },
        @{ content = "I disagree with your opinion, but I respect your right to have it."; description = "😐 Respectful disagreement" },
        @{ content = "The weather forecast shows rain for tomorrow."; description = "😐 Factual statement" },
        @{ content = "You're kind of annoying sometimes"; description = "⚠️ Mildly negative" },
        @{ content = "This is stupid and makes no sense"; description = "⚠️ Moderate negativity" },
        @{ content = "You are an idiot and I hate your opinion"; description = "🚨 Insulting language" },
        @{ content = "Go kill yourself, nobody likes you"; description = "🚨 Severe toxicity/harassment" },
        @{ content = "F**k this s**t, you're all morons"; description = "🚨 Profanity + insults" }
    )
    
    foreach ($test in $testCases) {
        Test-SingleContent -Content $test.content -Description $test.description
        Start-Sleep -Milliseconds 500  # Small delay for readability
    }
    
    # Batch testing
    Test-BatchContent
}

function Start-InteractiveMode {
    Write-Header "🎮 INTERACTIVE MODE"
    Write-ColorText "Enter text to check for toxicity. Type 'quit' to exit." -Color $Colors.Info
    Write-Host ""
    
    while ($true) {
        Write-Host "Enter content to analyze: " -NoNewline -ForegroundColor $Colors.Header
        $userInput = Read-Host
        
        if ($userInput -eq "quit" -or $userInput -eq "exit") {
            Write-ColorText "👋 Goodbye!" -Color $Colors.Success
            break
        }
        
        if ([string]::IsNullOrWhiteSpace($userInput)) {
            Write-ColorText "⚠️ Please enter some content to analyze." -Color $Colors.Warning
            continue
        }
        
        Write-Host ""
        Test-SingleContent -Content $userInput
    }
}

function Show-ServiceInfo {
    Write-Header "ℹ️ SERVICE INFORMATION"
    
    try {
        $response = Invoke-RestMethod -Uri "$ServiceUrl/api/moderation/info" -Method GET
        Write-ColorText "Detector Type: $($response.detector_type)" -Color $Colors.Info
        Write-ColorText "Version: $($response.version)" -Color $Colors.Info
        Write-ColorText "Framework: $($response.framework)" -Color $Colors.Info
        Write-ColorText "Model Name: $($response.model_name)" -Color $Colors.Info
        Write-ColorText "Description: $($response.description)" -Color $Colors.Info
    }
    catch {
        Write-ColorText "❌ Could not retrieve service info: $($_.Exception.Message)" -Color $Colors.Error
    }
}

# Main execution
Clear-Host
Write-ColorText @"
 ╔══════════════════════════════════════════════════════════════╗
 ║                    MODERATION SERVICE DEMO                    ║
 ║                                                              ║
 ║  This script demonstrates the AI-powered toxicity detection  ║
 ║  capabilities of our moderation service.                     ║
 ╚══════════════════════════════════════════════════════════════╝
"@ -Color $Colors.Header

Write-Host ""
Write-ColorText "🔗 Service URL: $ServiceUrl" -Color $Colors.Info
Write-Host ""

# Show service information
Show-ServiceInfo

if ($RunTests) {
    Run-DemoTests
}

if ($Interactive) {
    Start-InteractiveMode
} else {
    Write-Host ""
    Write-ColorText "💡 Tip: Run with -Interactive flag for interactive mode!" -Color $Colors.Info
    Write-ColorText "💡 Example: .\demo-moderation.ps1 -Interactive" -Color $Colors.Info
}

Write-Host ""
Write-ColorText "Demo completed!" -Color $Colors.Success
