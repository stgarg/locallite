#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Download BGE-small-en-v1.5 model with ONNX file from HuggingFace
.DESCRIPTION
    Downloads the complete bge-small-en-v1.5 model including model.onnx file
    from HuggingFace repository to make it usable for embedding inference.
#>

param(
    [string]$OutputDir = "models/bge-small-en-v1.5",
    [switch]$Force
)

$baseUrl = "https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main"
$files = @(
    @{ Name = "model.onnx"; Size = "~86MB"; Required = $true },
    @{ Name = "tokenizer.json"; Size = "~450KB"; Required = $true },
    @{ Name = "config.json"; Size = "~600B"; Required = $false },
    @{ Name = "tokenizer_config.json"; Size = "~500B"; Required = $false }
)

Write-Host "BGE-small-en-v1.5 Model Downloader" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Downloading to: $OutputDir" -ForegroundColor Yellow

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
    Write-Host "Created directory: $OutputDir" -ForegroundColor Green
}

# Check if model already exists
$modelPath = Join-Path $OutputDir "model.onnx"
if ((Test-Path $modelPath) -and -not $Force) {
    Write-Host "Model already exists at $modelPath" -ForegroundColor Yellow
    Write-Host "Use -Force to re-download" -ForegroundColor Yellow
    return
}

Write-Host "`nDownloading files..." -ForegroundColor Yellow

$totalFiles = $files.Count
$downloadedFiles = 0
$failedFiles = @()

foreach ($file in $files) {
    $fileName = $file.Name
    $fileSize = $file.Size
    $isRequired = $file.Required
    $url = "$baseUrl/$fileName"
    $outputPath = Join-Path $OutputDir $fileName
    
    Write-Host "`n[$($downloadedFiles + 1)/$totalFiles] Downloading $fileName ($fileSize)..." -ForegroundColor White
    
    try {
        # Use Invoke-WebRequest with progress
        $progressPreference = 'Continue'
        Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing
        
        if (Test-Path $outputPath) {
            $actualSize = [math]::Round((Get-Item $outputPath).Length / 1MB, 2)
            Write-Host "  ✅ Downloaded: $fileName (${actualSize}MB)" -ForegroundColor Green
            $downloadedFiles++
        } else {
            throw "File not created"
        }
    }
    catch {
        $errorMsg = "  ❌ Failed: $fileName - $($_.Exception.Message)"
        Write-Host $errorMsg -ForegroundColor Red
        
        if ($isRequired) {
            $failedFiles += $fileName
        } else {
            Write-Host "  ⚠️  Optional file, continuing..." -ForegroundColor Yellow
        }
    }
}

Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "DOWNLOAD SUMMARY" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Cyan

if ($failedFiles.Count -eq 0) {
    Write-Host "✅ SUCCESS: All files downloaded successfully!" -ForegroundColor Green
    Write-Host "Downloaded $downloadedFiles/$totalFiles files" -ForegroundColor Green
    
    # Verify essential files
    $modelExists = Test-Path (Join-Path $OutputDir "model.onnx")
    $tokenizerExists = Test-Path (Join-Path $OutputDir "tokenizer.json")
    
    if ($modelExists -and $tokenizerExists) {
        Write-Host "`n🎉 BGE model is ready for use!" -ForegroundColor Green
        Write-Host "Model location: $OutputDir" -ForegroundColor White
        
        # Show file sizes
        Write-Host "`nDownloaded files:" -ForegroundColor Yellow
        Get-ChildItem $OutputDir | ForEach-Object {
            $size = [math]::Round($_.Length / 1MB, 2)
            Write-Host "  $($_.Name): ${size}MB" -ForegroundColor White
        }
        
        Write-Host "`nTo use this model:" -ForegroundColor Yellow
        Write-Host "  `$env:EMB_MODEL_DIR = `"models/bge-small-en-v1.5`"" -ForegroundColor Cyan
        Write-Host "  .\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe" -ForegroundColor Cyan
        
        Write-Host "`nTo test the model:" -ForegroundColor Yellow
        Write-Host "  `$env:EMB_MODEL_DIR = `"models/bge-small-en-v1.5`"" -ForegroundColor Cyan
        Write-Host "  .\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe --health" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  Warning: Essential files missing" -ForegroundColor Yellow
        if (-not $modelExists) { Write-Host "  Missing: model.onnx" -ForegroundColor Red }
        if (-not $tokenizerExists) { Write-Host "  Missing: tokenizer.json" -ForegroundColor Red }
    }
} else {
    Write-Host "❌ FAILED: Some required files could not be downloaded" -ForegroundColor Red
    Write-Host "Failed files: $($failedFiles -join ', ')" -ForegroundColor Red
    Write-Host "`nTry running with -Force to retry downloads" -ForegroundColor Yellow
}

Write-Host "`nFor complete documentation, see INSTRUCTIONS.md" -ForegroundColor Gray