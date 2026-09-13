param([string]$Address)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Get-LANAddress.ps1')
if (-not $Address) { $Address = Get-VRLocalAddress }
$nodeProgram = (Get-Command node -ErrorAction Stop).Source
$statusDirectory = Join-Path (Split-Path -Parent $PSScriptRoot) '.local-vr'
New-Item -ItemType Directory -Force -Path $statusDirectory | Out-Null
try {
 if (-not (Get-NetFirewallRule -Name 'Komnata-VR-HTTPS-8443' -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -Name 'Komnata-VR-HTTPS-8443' -DisplayName 'Komnata VR - HTTPS w sieci domowej' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8443 -LocalAddress $Address -RemoteAddress LocalSubnet -Profile Private -Program $nodeProgram | Out-Null
 }
 'OK' | Set-Content (Join-Path (Split-Path -Parent $PSScriptRoot) '.local-vr/firewall-status.txt')
} catch {
 $_.Exception.Message | Set-Content (Join-Path (Split-Path -Parent $PSScriptRoot) '.local-vr/firewall-status.txt')
 exit 1
}
