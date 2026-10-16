[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$TemplatePath,
  [string]$Profile = "local-profile",
  [string]$Region = "us-east-1"
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $TemplatePath)) { throw "Template not found: $TemplatePath" }
$resolved = (Resolve-Path -LiteralPath $TemplatePath).Path
Write-Host "Calling CloudFormation validate-template; no resources will be created." -ForegroundColor Cyan
& aws cloudformation validate-template --template-body "file://$resolved" --profile $Profile --region $Region
if ($LASTEXITCODE -ne 0) { throw "CloudFormation validation failed." }
Write-Host "Validation passed. Live topology and change set still require review." -ForegroundColor Green
