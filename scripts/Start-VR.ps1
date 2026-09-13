param([string]$Address)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Get-LANAddress.ps1')
if (-not $Address) { $Address = Get-VRLocalAddress }
$projectRoot = Split-Path -Parent $PSScriptRoot
$certificateDir = Join-Path $projectRoot '.local-vr'
New-Item -ItemType Directory -Force -Path $certificateDir | Out-Null
$certificateFile = Join-Path $certificateDir 'cert.pem'
$keyFile = Join-Path $certificateDir 'key.pem'
$addressFile = Join-Path $certificateDir 'address.txt'
$renew = -not ((Test-Path $certificateFile) -and (Test-Path $keyFile) -and (Test-Path $addressFile))
if (-not $renew) {
 $existingCert = $null
 try {
  # The certificate and its private key are stored in separate PEM files.
  $existingCert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::CreateFromPemFile($certificateFile, $keyFile)
  $renew = ($existingCert.NotAfter -lt (Get-Date).AddDays(1)) -or ((Get-Content $addressFile -Raw).Trim() -ne $Address)
 } catch {
  Write-Host 'Nie można odczytać lokalnego certyfikatu. Tworzę nowy.'
  $renew = $true
 } finally {
  if ($null -ne $existingCert) { $existingCert.Dispose() }
 }
}
if ($renew) {
 $rsa = [System.Security.Cryptography.RSA]::Create(2048)
 $request = [System.Security.Cryptography.X509Certificates.CertificateRequest]::new('CN=Komnata VR local', $rsa, [System.Security.Cryptography.HashAlgorithmName]::SHA256, [System.Security.Cryptography.RSASignaturePadding]::Pkcs1)
 $san = [System.Security.Cryptography.X509Certificates.SubjectAlternativeNameBuilder]::new()
 $san.AddIpAddress([System.Net.IPAddress]::Parse($Address))
 $san.AddIpAddress([System.Net.IPAddress]::Loopback)
 $san.AddDnsName('localhost')
 $request.CertificateExtensions.Add($san.Build())
 $request.CertificateExtensions.Add([System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($false,$false,0,$true))
 $cert = $request.CreateSelfSigned([DateTimeOffset]::Now.AddMinutes(-5),[DateTimeOffset]::Now.AddDays(90))
 [System.IO.File]::WriteAllText($certificateFile,$cert.ExportCertificatePem())
 [System.IO.File]::WriteAllText($keyFile,$rsa.ExportPkcs8PrivateKeyPem())
 [System.IO.File]::WriteAllText($addressFile,$Address)
 $cert.Dispose(); $rsa.Dispose()
}
& node (Join-Path $PSScriptRoot 'serve-lan.cjs') $Address
exit $LASTEXITCODE
