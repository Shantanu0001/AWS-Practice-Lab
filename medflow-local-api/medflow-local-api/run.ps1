$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host 'Starting MedFlow local mock API at http://127.0.0.1:8000' -ForegroundColor Cyan
Write-Host 'Synthetic data only. Demo tenant switch is not authentication. Ctrl+C stops the server.' -ForegroundColor Yellow
python .\server.py
