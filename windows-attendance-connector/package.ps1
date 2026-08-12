param(
  [string]$Runtime = "win-x64",
  [string]$Configuration = "Release",
  [string]$CertificatePath = "",
  [string]$CertificatePassword = "",
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Publish = Join-Path $ProjectRoot "artifacts\publish"
$Output = Join-Path $ProjectRoot "artifacts\Lakshya-Attendance-Connector"

dotnet publish (Join-Path $ProjectRoot "Lakshya.Attendance.Connector.csproj") `
  -c $Configuration -r $Runtime --self-contained true `
  -p:PublishSingleFile=true -p:DebugType=None -o $Publish

if (Test-Path $Output) { Remove-Item $Output -Recurse -Force }
New-Item -ItemType Directory -Path $Output | Out-Null
Copy-Item (Join-Path $Publish "LakshyaAttendanceConnector.exe") $Output

if ($CertificatePath) {
  $SignTool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Filter signtool.exe -Recurse |
    Sort-Object FullName -Descending | Select-Object -First 1
  if (-not $SignTool) { throw "SignTool was not found. Install the Windows SDK." }
  & $SignTool.FullName sign /fd SHA256 /tr $TimestampUrl /td SHA256 /f $CertificatePath /p $CertificatePassword `
    (Join-Path $Output "LakshyaAttendanceConnector.exe")
  & $SignTool.FullName verify /pa /v (Join-Path $Output "LakshyaAttendanceConnector.exe")
} else {
  Write-Warning "The executable was built but is NOT signed. Do not distribute it as a production installer."
}

Write-Host "Connector output: $Output"
