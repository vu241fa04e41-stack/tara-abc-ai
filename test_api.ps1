param(
  [string]$BaseUrl = "http://127.0.0.1:5000"
)

Write-Host "Health:"
Invoke-RestMethod "$BaseUrl/api/health" | ConvertTo-Json

Write-Host "`nSummary:"
Invoke-RestMethod "$BaseUrl/api/summary" | ConvertTo-Json

Write-Host "`nCameras:"
Invoke-RestMethod "$BaseUrl/api/cameras" | ConvertTo-Json
