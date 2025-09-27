# EmbeddingServer API Test Suite
# 
# This script validates all API endpoints and functionality
# Run this after starting your EmbeddingServer to ensure everything works
#
# Usage: .\scripts\test-api.ps1 [-ServerUrl "http://localhost:8080"] [-Verbose]

param(
    [string]$ServerUrl = "http://localhost:8080",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-TestResult {
    param($Name, $Success, $Details = "")
    
    if ($Success) {
        Write-Host "✅ $Name" -ForegroundColor Green
        if ($Verbose -and $Details) {
            Write-Host "   $Details" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ $Name" -ForegroundColor Red
        if ($Details) {
            Write-Host "   $Details" -ForegroundColor Red
        }
    }
}

function Test-ApiEndpoint {
    param($Name, $ScriptBlock)
    
    Write-Host "Testing $Name..." -ForegroundColor Yellow
    try {
        $result = & $ScriptBlock
        Write-TestResult $Name $true $(if ($Verbose) { "Result: $($result | ConvertTo-Json -Compress -Depth 2)" } else { "" })
        return @{ Success = $true; Result = $result }
    }
    catch {
        Write-TestResult $Name $false $_.Exception.Message
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

Write-Host "🚀 EmbeddingServer API Test Suite" -ForegroundColor Cyan
Write-Host "Testing server at: $ServerUrl" -ForegroundColor Cyan
Write-Host "=" * 50

$tests = 0
$passed = 0
$results = @{}

# Test 1: Server Connectivity
$test = Test-ApiEndpoint "Server Connectivity" {
    try {
        $response = Invoke-WebRequest -Uri $ServerUrl -Method Head -TimeoutSec 5
        return @{ Status = $response.StatusCode; Available = $true }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            return @{ Status = 404; Available = $true; Note = "Server responding but no root endpoint" }
        }
        throw
    }
}
$results.Connectivity = $test
if ($test.Success) { $passed++ }
$tests++

# Test 2: Health Check Endpoint
$test = Test-ApiEndpoint "Health Check Endpoint" {
    $health = Invoke-RestMethod -Uri "$ServerUrl/healthz" -Method Get
    if ($health.status -ne "ok") { 
        throw "Status is '$($health.status)', expected 'ok'" 
    }
    return @{
        Status = $health.status
        Model = $health.model
        Dimension = $health.dimension
        ExecutionProvider = $health.executionProvider
        Mock = $health.mock
    }
}
$results.HealthCheck = $test
if ($test.Success) { $passed++ }
$tests++

# Test 3: Single Text Embedding
$test = Test-ApiEndpoint "Single Text Embedding" {
    $body = @{ text = "Hello world" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$ServerUrl/embed" -Method Post -Body $body -ContentType "application/json"
    
    if ($result.count -ne 1) { throw "Expected count=1, got $($result.count)" }
    if ($result.embeddings.Count -ne 1) { throw "Expected 1 embedding, got $($result.embeddings.Count)" }
    if ($result.embeddings[0].Count -ne $result.dimension) { 
        throw "Embedding size ($($result.embeddings[0].Count)) doesn't match dimension ($($result.dimension))" 
    }
    
    return @{
        Dimension = $result.dimension
        VectorLength = $result.embeddings[0].Count
        TokenCount = $result.tokensPerInput[0]
        Model = $result.model
        Pooling = $result.pooling
        Normalized = $result.normalized
    }
}
$results.SingleEmbedding = $test
if ($test.Success) { $passed++ }
$tests++

# Test 4: Batch Embedding
$test = Test-ApiEndpoint "Batch Embedding" {
    $texts = @("First text", "Second text", "Third text")
    $body = @{ texts = $texts } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$ServerUrl/embed" -Method Post -Body $body -ContentType "application/json"
    
    if ($result.count -ne 3) { throw "Expected count=3, got $($result.count)" }
    if ($result.embeddings.Count -ne 3) { throw "Expected 3 embeddings, got $($result.embeddings.Count)" }
    
    # Verify all embeddings have correct dimension
    for ($i = 0; $i -lt $result.embeddings.Count; $i++) {
        if ($result.embeddings[$i].Count -ne $result.dimension) {
            throw "Embedding $i size ($($result.embeddings[$i].Count)) doesn't match dimension ($($result.dimension))"
        }
    }
    
    return @{
        Count = $result.count
        Dimension = $result.dimension
        TokenCounts = $result.tokensPerInput -join ", "
    }
}
$results.BatchEmbedding = $test
if ($test.Success) { $passed++ }
$tests++

# Test 5: Error Handling - Empty Request
$test = Test-ApiEndpoint "Error Handling (Empty Request)" {
    try {
        $body = @{} | ConvertTo-Json
        $result = Invoke-RestMethod -Uri "$ServerUrl/embed" -Method Post -Body $body -ContentType "application/json"
        throw "Request should have failed but succeeded"
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            # Try to get error message
            try {
                $errorStream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorStream)
                $errorBody = $reader.ReadToEnd()
                $errorJson = $errorBody | ConvertFrom-Json
                return @{ 
                    StatusCode = 400
                    ErrorMessage = $errorJson.error
                    Handled = $true
                }
            } catch {
                return @{ 
                    StatusCode = 400
                    ErrorMessage = "Bad Request (details unavailable)"
                    Handled = $true
                }
            }
        }
        throw
    }
}
$results.ErrorHandling = $test
if ($test.Success) { $passed++ }
$tests++

# Test 6: Multilingual Support (if available)
$test = Test-ApiEndpoint "Multilingual Support" {
    $multilingualTexts = @(
        "Hello world",      # English
        "नमस्ते दुनिया",     # Hindi
        "Bonjour le monde"  # French
    )
    
    $body = @{ texts = $multilingualTexts } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$ServerUrl/embed" -Method Post -Body $body -ContentType "application/json"
    
    if ($result.count -ne 3) { throw "Expected count=3 for multilingual test" }
    
    return @{
        Count = $result.count
        Model = $result.model
        Languages = "English, Hindi, French"
        Success = $true
    }
}
$results.Multilingual = $test
if ($test.Success) { $passed++ }
$tests++

# Test 7: Performance Test (Simple)
$test = Test-ApiEndpoint "Performance Test" {
    $text = "This is a performance test sentence with multiple words to measure embedding speed."
    $body = @{ text = $text } | ConvertTo-Json
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $result = Invoke-RestMethod -Uri "$ServerUrl/embed" -Method Post -Body $body -ContentType "application/json"
    $stopwatch.Stop()
    
    $latencyMs = $stopwatch.ElapsedMilliseconds
    
    return @{
        LatencyMs = $latencyMs
        TokenCount = $result.tokensPerInput[0]
        Dimension = $result.dimension
        Status = if ($latencyMs -lt 1000) { "Good" } elseif ($latencyMs -lt 5000) { "Acceptable" } else { "Slow" }
    }
}
$results.Performance = $test
if ($test.Success) { $passed++ }
$tests++

# Summary
Write-Host ""
Write-Host "=" * 50
Write-Host "🏁 Test Results Summary" -ForegroundColor Cyan
Write-Host "Passed: $passed / $tests tests" -ForegroundColor $(if ($passed -eq $tests) { "Green" } else { "Yellow" })

if ($passed -eq $tests) {
    Write-Host "🎉 All tests passed! Your EmbeddingServer is working correctly." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the details above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Test Details:" -ForegroundColor Cyan

if ($results.HealthCheck.Success) {
    $health = $results.HealthCheck.Result
    Write-Host "• Model: $($health.Model)" -ForegroundColor White
    Write-Host "• Dimension: $($health.Dimension)" -ForegroundColor White
    Write-Host "• Execution Provider: $($health.ExecutionProvider)" -ForegroundColor White
    Write-Host "• Mock Mode: $($health.Mock)" -ForegroundColor White
}

if ($results.Performance.Success) {
    $perf = $results.Performance.Result
    Write-Host "• Latency: $($perf.LatencyMs)ms ($($perf.Status))" -ForegroundColor White
}

if ($results.SingleEmbedding.Success) {
    $embed = $results.SingleEmbedding.Result
    Write-Host "• Pooling: $($embed.Pooling)" -ForegroundColor White
    Write-Host "• Normalized: $($embed.Normalized)" -ForegroundColor White
}

Write-Host ""
Write-Host "💡 Next Steps:" -ForegroundColor Cyan

if ($passed -eq $tests) {
    Write-Host "• Your server is ready for production use!" -ForegroundColor Green
    Write-Host "• See API_DOCUMENTATION.md for integration examples" -ForegroundColor White
    Write-Host "• Run .\scripts\benchmark-current-model.ps1 for detailed performance testing" -ForegroundColor White
} else {
    Write-Host "• Check server logs for error details" -ForegroundColor Yellow
    Write-Host "• Verify model files are present and correct" -ForegroundColor Yellow
    Write-Host "• See INSTRUCTIONS.md troubleshooting section" -ForegroundColor Yellow
}

# Return exit code
if ($passed -eq $tests) {
    exit 0
} else {
    exit 1
}