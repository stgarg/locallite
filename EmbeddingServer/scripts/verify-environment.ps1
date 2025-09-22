Write-Host '=== Architecture ==='
Write-Host "PROCESSOR_ARCHITECTURE=$env:PROCESSOR_ARCHITECTURE"
Write-Host "Is64BitOS=" ([Environment]::Is64BitOperatingSystem)

Write-Host '=== .NET Info (RID) ==='
dotnet --info | Select-String 'RID'

Write-Host '=== CPU Info ==='
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

Write-Host '=== DONE ==='
