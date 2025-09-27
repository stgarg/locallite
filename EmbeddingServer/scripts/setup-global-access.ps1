# Setup Global Access for EmbeddingServer
# This script adds EmbeddingServer.exe to the system PATH permanently

$ErrorActionPreference = "Stop"

Write-Host "Setting up global access for EmbeddingServer..." -ForegroundColor Green

# Get the current script directory and build path to executable
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ExePath = Join-Path $ProjectRoot "src\bin\Debug\net8.0\win-arm64"

# Verify the executable exists
$ExeFile = Join-Path $ExePath "EmbeddingServer.exe"
if (-not (Test-Path $ExeFile)) {
    Write-Host "❌ EmbeddingServer.exe not found at: $ExeFile" -ForegroundColor Red
    Write-Host "   Please build the project first with: dotnet build -c Debug" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found EmbeddingServer.exe at: $ExePath" -ForegroundColor Green

# Get current user PATH
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Check if already in PATH
if ($CurrentPath -like "*$ExePath*") {
    Write-Host "✅ EmbeddingServer is already in your PATH" -ForegroundColor Green
} else {
    # Add to user PATH (doesn't require admin rights)
    $NewPath = $CurrentPath + ";" + $ExePath
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "✅ Added EmbeddingServer to your PATH" -ForegroundColor Green
    Write-Host "   Restart your terminal or run: refreshenv" -ForegroundColor Yellow
}

# Test the setup
Write-Host "`nTesting global access..." -ForegroundColor Cyan
try {
    # Update PATH for current session
    $env:PATH += ";$ExePath"
    
    # Test if it works
    $TestOutput = & EmbeddingServer.exe --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Global access test successful!" -ForegroundColor Green
        Write-Host "`nYou can now use these commands from anywhere:" -ForegroundColor Cyan
        Write-Host "  EmbeddingServer.exe --help      # Show help"
        Write-Host "  EmbeddingServer.exe --health    # Check health"
        Write-Host "  EmbeddingServer.exe --text 'hi' # Get embedding"
        Write-Host "  EmbeddingServer.exe             # Start server"
    } else {
        Write-Host "❌ Global access test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing global access: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Setup complete! EmbeddingServer is now globally accessible." -ForegroundColor Green