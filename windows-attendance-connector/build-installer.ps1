param(
  [Parameter(Mandatory=$true)][string]$CertificatePath,
  [Parameter(Mandatory=$true)][string]$CertificatePassword,
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $Root "package.ps1") -CertificatePath $CertificatePath -CertificatePassword $CertificatePassword -TimestampUrl $TimestampUrl

$Compiler = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if (-not $Compiler) {
  $Default = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
  if (Test-Path $Default) { $Compiler = $Default }
}
if (-not $Compiler) { throw "Inno Setup 6 was not found." }
$CompilerPath = if ($Compiler -is [System.Management.Automation.CommandInfo]) { $Compiler.Source } else { [string]$Compiler }
& $CompilerPath (Join-Path $Root "installer.iss")

$Setup = Join-Path $Root "artifacts\Lakshya-Attendance-Connector-Setup.exe"
$SignTool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Filter signtool.exe -Recurse |
  Sort-Object FullName -Descending | Select-Object -First 1
if (-not $SignTool) { throw "SignTool was not found. Install the Windows SDK." }
& $SignTool.FullName sign /fd SHA256 /tr $TimestampUrl /td SHA256 /f $CertificatePath /p $CertificatePassword $Setup
& $SignTool.FullName verify /pa /v $Setup
$Application = Join-Path $Root "artifacts\Lakshya-Attendance-Connector\LakshyaAttendanceConnector.exe"
& $SignTool.FullName verify /pa /v $Application
$Checksums = @(
  "$(Get-FileHash $Setup -Algorithm SHA256 | Select-Object -ExpandProperty Hash)  $(Split-Path $Setup -Leaf)",
  "$(Get-FileHash $Application -Algorithm SHA256 | Select-Object -ExpandProperty Hash)  $(Split-Path $Application -Leaf)"
)
$Checksums | Set-Content (Join-Path $Root "artifacts\SHA256SUMS.txt") -Encoding ascii
Write-Host "Signed installer: $Setup"
