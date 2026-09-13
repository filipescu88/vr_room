function Get-VRLocalAddress {
 foreach ($adapter in [System.Net.NetworkInformation.NetworkInterface]::GetAllNetworkInterfaces()) {
  if ($adapter.OperationalStatus -ne 'Up' -or $adapter.NetworkInterfaceType -eq 'Loopback') { continue }
  $properties = $adapter.GetIPProperties()
  if (-not @($properties.GatewayAddresses | Where-Object { $_.Address.AddressFamily -eq 'InterNetwork' -and $_.Address.ToString() -ne '0.0.0.0' }).Count) { continue }
  foreach ($entry in $properties.UnicastAddresses) {
   if ($entry.Address.AddressFamily -eq 'InterNetwork') { return $entry.Address.ToString() }
  }
 }
 throw 'Nie znaleziono adresu sieci lokalnej. Podaj -Address ADRES_IP.'
}
