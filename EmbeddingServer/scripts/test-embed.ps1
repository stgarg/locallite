Param(
  [string]$ListenHost = "127.0.0.1",
  [int]$Port = 8080,
  [switch]$Start,
  [switch]$Mock,
  [int]$Dim = 12
)

$base = "http://$ListenHost`:$Port"

function Invoke-JsonPost($url, $obj) {
  $json = $obj | ConvertTo-Json -Depth 6 -Compress
  return Invoke-RestMethod -Method Post -Uri $url -Body $json -ContentType 'application/json'
}

if ($Start) {
  if ($Mock) { $env:EMB_MOCK='1'; $env:EMB_MOCK_DIM = "$Dim" }
  $env:EMB_PORT = "$Port"
  Write-Host "[test-embed] Starting server (Mock=$Mock Port=$Port) ..." -ForegroundColor Cyan
  Start-Process -NoNewWindow -FilePath dotnet -ArgumentList "run --project ..\src\EmbeddingServer.csproj" | Out-Null
  Start-Sleep -Seconds 3
}

Write-Host "[test-embed] GET /healthz" -ForegroundColor Yellow
try {
  $health = Invoke-RestMethod -Uri "$base/healthz" -TimeoutSec 10
  $health | ConvertTo-Json -Depth 6
} catch {
  Write-Error "Health check failed: $_"; exit 1
}

Write-Host "[test-embed] POST /embed single" -ForegroundColor Yellow
$single = Invoke-JsonPost "$base/embed" @{ text = "quick brown fox" }
$single | ConvertTo-Json -Depth 6

Write-Host "[test-embed] POST /embed batch" -ForegroundColor Yellow
$batch = Invoke-JsonPost "$base/embed" @{ texts = @('lorem ipsum','second example phrase','short') }
$batch | ConvertTo-Json -Depth 6

Write-Host "[test-embed] Summary" -ForegroundColor Green
"Single dim=$($single.dimension) count=$($single.count) vectorLen=$($single.embeddings[0].Length)"
"Batch dim=$($batch.dimension) count=$($batch.count) lens=$(($batch.embeddings | ForEach-Object { $_.Length }) -join ',')"
