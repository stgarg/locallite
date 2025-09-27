#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Downloads pre-converted multilingual-e5-small ONNX model from HuggingFace
#>

param(
    [string]$ModelDir = "models/multilingual-e5-small",
    [switch]$Force = $false
)

$BaseDir = Split-Path -Parent $PSScriptRoot
$FullModelDir = Join-Path $BaseDir $ModelDir
$BaseUrl = "https://huggingface.co/intfloat/multilingual-e5-small/resolve/main"

Write-Host "Downloading multilingual-e5-small (pre-converted ONNX)" -ForegroundColor Cyan
Write-Host "Source: HuggingFace pre-built ONNX models" -ForegroundColor Gray
Write-Host "Target: $FullModelDir" -ForegroundColor Gray

# Check if model already exists
if ((Test-Path $FullModelDir) -and !$Force) {
    Write-Host "Model directory already exists. Use -Force to overwrite." -ForegroundColor Yellow
    exit 0
}

# Create model directory
New-Item -ItemType Directory -Path $FullModelDir -Force | Out-Null

# Files to download
$filesToDownload = @{
    "config.json" = "$BaseUrl/config.json"
    "tokenizer.json" = "$BaseUrl/tokenizer.json" 
    "tokenizer_config.json" = "$BaseUrl/tokenizer_config.json"
    "vocab.txt" = "$BaseUrl/vocab.txt"
    "model.onnx" = "$BaseUrl/onnx/model.onnx"  # Pre-converted ONNX!
}

Write-Host "`nDownloading model files..." -ForegroundColor Cyan

foreach ($file in $filesToDownload.Keys) {
    $url = $filesToDownload[$file]
    $outputPath = Join-Path $FullModelDir $file
    
    Write-Host "  Downloading $file..." -ForegroundColor Yellow
    
    try {
        # Download with progress
        $response = Invoke-WebRequest -Uri $url -OutFile $outputPath -PassThru
        
        if (Test-Path $outputPath) {
            $size = (Get-Item $outputPath).Length
            $sizeMB = [math]::Round($size / 1MB, 1)
            Write-Host "    Success: $sizeMB MB" -ForegroundColor Green
        } else {
            Write-Host "    Failed: File not created" -ForegroundColor Red
        }
    } catch {
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verify download
Write-Host "`nVerifying download..." -ForegroundColor Cyan
$requiredFiles = @("config.json", "tokenizer.json", "tokenizer_config.json", "vocab.txt", "model.onnx")
$allFilesPresent = $true

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $FullModelDir $file
    if (Test-Path $filePath) {
        $size = (Get-Item $filePath).Length
        $sizeMB = [math]::Round($size / 1MB, 1)
        Write-Host "  $file - $sizeMB MB" -ForegroundColor Green
    } else {
        Write-Host "  $file - MISSING" -ForegroundColor Red
        $allFilesPresent = $false
    }
}

if ($allFilesPresent) {
    Write-Host "`nDownload completed successfully!" -ForegroundColor Green
    
    # Show total size
    $totalSize = (Get-ChildItem $FullModelDir -Recurse | Measure-Object -Property Length -Sum).Sum
    $totalSizeMB = [math]::Round($totalSize / 1MB, 1)
    Write-Host "Total model size: $totalSizeMB MB" -ForegroundColor Cyan
    
    Write-Host "`nModel Information:" -ForegroundColor Yellow
    Write-Host "  Name: multilingual-e5-small"
    Write-Host "  Languages: 100+ including all major Indian languages"
    Write-Host "  Dimensions: 384 (same as current model)"
    Write-Host "  Format: Pre-converted ONNX (no build tools needed!)"
    Write-Host "  Performance: Better cross-lingual understanding"
    
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Stop current embedding server"
    Write-Host "  2. Set environment variable: `$env:EMB_MODEL_DIR = '$ModelDir'"
    Write-Host "  3. Restart embedding server"
    Write-Host "  4. Test with: .\scripts\test-multilingual-success.ps1"
    
} else {
    Write-Host "`nDownload incomplete. Some files are missing." -ForegroundColor Red
    exit 1
}