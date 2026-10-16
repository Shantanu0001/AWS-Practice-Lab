[CmdletBinding()]
param(
  [string]$Profile = "local-profile",
  [string]$Region = "us-east-1",
  [Parameter(Mandatory=$true)][string]$VpcId,
  [Parameter(Mandatory=$true)][string]$PublicSubnetA,
  [Parameter(Mandatory=$true)][string]$PublicSubnetB,
  [Parameter(Mandatory=$true)][string]$AppSubnetA,
  [Parameter(Mandatory=$true)][string]$AppSubnetB
)
$ErrorActionPreference = "Stop"
function AwsJson([string[]]$ArgsList) {
  $raw = & aws @ArgsList --profile $Profile --region $Region --output json
  if ($LASTEXITCODE -ne 0) { throw "AWS CLI command failed: aws $($ArgsList -join ' ')" }
  return ($raw | ConvertFrom-Json)
}
Write-Host "`n=== READ-ONLY STAGE 3 NETWORK PREFLIGHT ===" -ForegroundColor Cyan
Write-Host "This script makes no AWS changes." -ForegroundColor Green
$vpc = AwsJson @("ec2","describe-vpcs","--vpc-ids",$VpcId)
if ($vpc.Vpcs.Count -ne 1) { throw "VPC not found or ambiguous: $VpcId" }
$ids = @($PublicSubnetA,$PublicSubnetB,$AppSubnetA,$AppSubnetB)
$subnets = AwsJson (@("ec2","describe-subnets","--subnet-ids") + $ids)
$byId = @{}
foreach ($s in $subnets.Subnets) { $byId[$s.SubnetId] = $s }
foreach ($id in $ids) {
  if (-not $byId.ContainsKey($id)) { throw "Subnet not found: $id" }
  if ($byId[$id].VpcId -ne $VpcId) { throw "Subnet $id is not in $VpcId" }
}
if ($byId[$PublicSubnetA].AvailabilityZone -eq $byId[$PublicSubnetB].AvailabilityZone) { throw "Public subnets are in the same AZ." }
if ($byId[$AppSubnetA].AvailabilityZone -eq $byId[$AppSubnetB].AvailabilityZone) { throw "App subnets are in the same AZ." }
if ($byId[$PublicSubnetA].AvailabilityZone -ne $byId[$AppSubnetA].AvailabilityZone) { throw "Public-A and App-A are not in the same AZ." }
if ($byId[$PublicSubnetB].AvailabilityZone -ne $byId[$AppSubnetB].AvailabilityZone) { throw "Public-B and App-B are not in the same AZ." }

$rtResult = AwsJson @("ec2","describe-route-tables","--filters","Name=vpc-id,Values=$VpcId")
$rts = $rtResult.RouteTables
$main = $rts | Where-Object { $_.Associations | Where-Object { $_.Main -eq $true } } | Select-Object -First 1
if (-not $main) { throw "Could not identify the main route table." }
function RouteTableFor([string]$SubnetId) {
  $m = @($rts | Where-Object { $_.Associations | Where-Object { $_.SubnetId -eq $SubnetId } })
  if ($m.Count -gt 1) { throw "Multiple route-table associations for $SubnetId" }
  if ($m.Count -eq 1) { return $m[0] }
  return $main
}
function DefaultRoute($rt) { return ($rt.Routes | Where-Object { $_.DestinationCidrBlock -eq "0.0.0.0/0" } | Select-Object -First 1) }

$map = @(
  [pscustomobject]@{Tier="Public-A";Subnet=$PublicSubnetA;AZ=$byId[$PublicSubnetA].AvailabilityZone;RT=(RouteTableFor $PublicSubnetA)},
  [pscustomobject]@{Tier="Public-B";Subnet=$PublicSubnetB;AZ=$byId[$PublicSubnetB].AvailabilityZone;RT=(RouteTableFor $PublicSubnetB)},
  [pscustomobject]@{Tier="App-A";Subnet=$AppSubnetA;AZ=$byId[$AppSubnetA].AvailabilityZone;RT=(RouteTableFor $AppSubnetA)},
  [pscustomobject]@{Tier="App-B";Subnet=$AppSubnetB;AZ=$byId[$AppSubnetB].AvailabilityZone;RT=(RouteTableFor $AppSubnetB)}
)
Write-Host "`n=== SUBNET / ROUTE TABLE MAPPING ===" -ForegroundColor Cyan
$map | ForEach-Object {
  $d = DefaultRoute $_.RT
  $target = if (-not $d) {"(none)"} elseif ($d.GatewayId) {$d.GatewayId} elseif ($d.NatGatewayId) {$d.NatGatewayId} else {"other target"}
  [pscustomobject]@{Tier=$_.Tier;SubnetId=$_.Subnet;AZ=$_.AZ;RouteTableId=$_.RT.RouteTableId;DefaultRouteTarget=$target}
} | Format-Table -AutoSize

$failures = [System.Collections.Generic.List[string]]::new()
$pubA = DefaultRoute (RouteTableFor $PublicSubnetA)
$pubB = DefaultRoute (RouteTableFor $PublicSubnetB)
$rtA = RouteTableFor $AppSubnetA
$rtB = RouteTableFor $AppSubnetB
if (-not $pubA -or $pubA.GatewayId -notlike "igw-*") { $failures.Add("Public-A must have 0.0.0.0/0 -> IGW.") }
if (-not $pubB -or $pubB.GatewayId -notlike "igw-*") { $failures.Add("Public-B must have 0.0.0.0/0 -> IGW.") }
if ($rtA.RouteTableId -eq $rtB.RouteTableId) { $failures.Add("App-A and App-B share $($rtA.RouteTableId). Stop: two NAT routes cannot be added to one route table.") }
if (DefaultRoute $rtA) { $failures.Add("App-A route table already has a 0.0.0.0/0 route.") }
if (DefaultRoute $rtB) { $failures.Add("App-B route table already has a 0.0.0.0/0 route.") }

Write-Host "`n=== NAT GATEWAY INVENTORY ===" -ForegroundColor Cyan
$nats = AwsJson @("ec2","describe-nat-gateways","--filter","Name=vpc-id,Values=$VpcId")
if (-not $nats.NatGateways -or $nats.NatGateways.Count -eq 0) { Write-Host "No NAT Gateways returned." }
else { $nats.NatGateways | Select-Object NatGatewayId,State,SubnetId | Format-Table -AutoSize }

if ($failures.Count) {
  Write-Host "`nPREFLIGHT: BLOCKED" -ForegroundColor Red
  $failures | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
  exit 2
}
Write-Host "`nPREFLIGHT: PASS for checked conditions only." -ForegroundColor Green
Write-Host "Observed route-table IDs for review only: App-A=$($rtA.RouteTableId); App-B=$($rtB.RouteTableId)"
Write-Host "This is not deployment approval. Review cost, change set, runtime limit, and teardown first."
