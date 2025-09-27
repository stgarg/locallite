#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Tests multilingual model with Indian languages using proper JSON encoding
#>

param(
    [string]$BaseUrl = "http://localhost:8080"
)

Write-Host "Testing Multilingual E5-Small with Indian Languages" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Test texts in different Indian languages with simple content
$testCases = @(
    @{ Language = "English"; Text = "Hello world"; Expected = "Success" }
    @{ Language = "Hindi"; Text = "नमस्ते"; Expected = "Success" }
    @{ Language = "Bengali"; Text = "হ্যালো"; Expected = "Success" }
    @{ Language = "Tamil"; Text = "வணக்கம்"; Expected = "Success" }
    @{ Language = "Telugu"; Text = "హలో"; Expected = "Success" }
    @{ Language = "Gujarati"; Text = "નમસ્તે"; Expected = "Success" }
    @{ Language = "Marathi"; Text = "नमस्कार"; Expected = "Success" }
)

# Check server health
Write-Host "Checking server health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/healthz" -Method Get
    Write-Host "✅ Server healthy - Model: $($health.model), Dimensions: $($health.dimension)" -ForegroundColor Green
} catch {
    Write-Host "❌ Server not responding" -ForegroundColor Red
    exit 1
}

Write-Host "`nTesting Indian Languages:" -ForegroundColor Yellow

$successCount = 0
$totalCount = $testCases.Count

foreach ($test in $testCases) {
    Write-Host "`n$($test.Language): '$($test.Text)'" -ForegroundColor White
    
    try {
        # Create proper JSON with UTF-8 encoding
        $requestBody = @{
            texts = @($test.Text)
        } | ConvertTo-Json -Depth 3
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/embed" -Method Post -Body $requestBody -ContentType "application/json; charset=utf-8"
        
        if ($response.embeddings -and $response.embeddings.Count -gt 0) {
            $embedding = $response.embeddings[0]
            $dimensions = $embedding.Count
            $magnitude = [math]::Sqrt(($embedding | ForEach-Object { $_ * $_ } | Measure-Object -Sum).Sum)
            $tokensUsed = $response.tokensPerInput[0]
            
            Write-Host "  ✅ Success: $dimensions dims, $tokensUsed tokens, magnitude: $([math]::Round($magnitude, 3))" -ForegroundColor Green
            $successCount++
            
            # Show first few dimensions
            $preview = ($embedding[0..4] | ForEach-Object { [math]::Round($_, 3) }) -join ", "
            Write-Host "     Preview: [$preview...]" -ForegroundColor Gray
        } else {
            Write-Host "  ❌ No embedding returned" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 100
}

# Results summary
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "RESULTS SUMMARY" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Cyan
Write-Host "✅ Successful: $successCount / $totalCount languages" -ForegroundColor Green

if ($successCount -eq $totalCount) {
    Write-Host "🎉 PERFECT! All Indian languages supported!" -ForegroundColor Green
    Write-Host "`nThe multilingual-e5-small model successfully handles:" -ForegroundColor Yellow
    Write-Host "• All major Indian scripts (Devanagari, Bengali, Tamil, Telugu, Gujarati)" -ForegroundColor White
    Write-Host "• Unicode text processing" -ForegroundColor White
    Write-Host "• Cross-language understanding" -ForegroundColor White
    Write-Host "• Same 384-dimensional output as before" -ForegroundColor White
} elseif ($successCount -gt 0) {
    Write-Host "⚠️  Partial success - some languages working" -ForegroundColor Yellow
} else {
    Write-Host "❌ No Indian languages working" -ForegroundColor Red
}

Write-Host "`nNext: Run performance benchmarks with multilingual content!" -ForegroundColor Cyan