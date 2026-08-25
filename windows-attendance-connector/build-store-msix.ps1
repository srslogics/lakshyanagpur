param(
  [string]$Version = "1.0.0.0",
  [string]$Configuration = "Release",
  [string]$TestCertificatePath = "",
  [string]$TestCertificatePassword = "",
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
if ($Version -notmatch '^\d+\.\d+\.\d+\.\d+$') {
  throw "MSIX version must contain four numeric parts, for example 1.0.0.0."
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepositoryRoot = Split-Path -Parent $Root
$Artifacts = Join-Path $Root "artifacts"
$Publish = Join-Path $Artifacts "store-publish"
$Layout = Join-Path $Artifacts "msix-layout"
$Assets = Join-Path $Layout "Assets"
$Package = Join-Path $Artifacts "Lakshya-Attendance-Connector_$($Version)_x64.msix"
$ManifestTemplate = Join-Path $Root "msix\AppxManifest.xml"
$BrandLogo = Join-Path $RepositoryRoot "lakshya-logo-576.png"

if (-not (Test-Path $BrandLogo)) { throw "Brand logo was not found: $BrandLogo" }
if (Test-Path $Publish) { Remove-Item $Publish -Recurse -Force }
if (Test-Path $Layout) { Remove-Item $Layout -Recurse -Force }
New-Item -ItemType Directory -Path $Publish, $Layout, $Assets -Force | Out-Null

dotnet publish (Join-Path $Root "Lakshya.Attendance.Connector.csproj") `
  -c $Configuration -r win-x64 --self-contained true `
  -p:PublishSingleFile=true -p:DebugType=None -p:Version=$Version -o $Publish
if ($LASTEXITCODE -ne 0) { throw "dotnet publish failed with exit code $LASTEXITCODE." }

Copy-Item (Join-Path $Publish "LakshyaAttendanceConnector.exe") $Layout

$Manifest = (Get-Content $ManifestTemplate -Raw).Replace("__VERSION__", $Version)
[System.IO.File]::WriteAllText(
  (Join-Path $Layout "AppxManifest.xml"),
  $Manifest,
  [System.Text.UTF8Encoding]::new($false))

Add-Type -AssemblyName System.Drawing
function New-LogoAsset {
  param([string]$Path, [int]$Width, [int]$Height)

  $Canvas = New-Object System.Drawing.Bitmap($Width, $Height)
  $Graphics = [System.Drawing.Graphics]::FromImage($Canvas)
  $Source = [System.Drawing.Image]::FromFile($BrandLogo)
  try {
    $Graphics.Clear([System.Drawing.Color]::White)
    $Graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $Graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $Graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $Padding = [Math]::Max(4, [Math]::Floor([Math]::Min($Width, $Height) * 0.12))
    $Scale = [Math]::Min(
      ($Width - (2 * $Padding)) / $Source.Width,
      ($Height - (2 * $Padding)) / $Source.Height)
    $DrawWidth = [Math]::Max(1, [int][Math]::Round($Source.Width * $Scale))
    $DrawHeight = [Math]::Max(1, [int][Math]::Round($Source.Height * $Scale))
    $X = [int](($Width - $DrawWidth) / 2)
    $Y = [int](($Height - $DrawHeight) / 2)
    $Graphics.DrawImage($Source, $X, $Y, $DrawWidth, $DrawHeight)
    $Canvas.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
  }
  finally {
    $Source.Dispose()
    $Graphics.Dispose()
    $Canvas.Dispose()
  }
}

New-LogoAsset (Join-Path $Assets "StoreLogo.png") 50 50
New-LogoAsset (Join-Path $Assets "Square44x44Logo.png") 44 44
New-LogoAsset (Join-Path $Assets "Square150x150Logo.png") 150 150
New-LogoAsset (Join-Path $Assets "Wide310x150Logo.png") 310 150
New-LogoAsset (Join-Path $Assets "Square310x310Logo.png") 310 310

$SdkBin = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
$MakeAppx = Get-ChildItem $SdkBin -Filter makeappx.exe -Recurse |
  Where-Object { $_.FullName -match '\\x64\\makeappx\.exe$' } |
  Sort-Object FullName -Descending | Select-Object -First 1
if (-not $MakeAppx) { throw "MakeAppx was not found. Install the Windows 10/11 SDK." }

if (Test-Path $Package) { Remove-Item $Package -Force }
& $MakeAppx.FullName pack /d $Layout /p $Package /o
if ($LASTEXITCODE -ne 0) { throw "MakeAppx failed with exit code $LASTEXITCODE." }

if ($TestCertificatePath) {
  $SignTool = Get-ChildItem $SdkBin -Filter signtool.exe -Recurse |
    Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
    Sort-Object FullName -Descending | Select-Object -First 1
  if (-not $SignTool) { throw "SignTool was not found. Install the Windows 10/11 SDK." }
  & $SignTool.FullName sign /fd SHA256 /tr $TimestampUrl /td SHA256 /f $TestCertificatePath /p $TestCertificatePassword $Package
  if ($LASTEXITCODE -ne 0) { throw "Signing failed. The certificate subject must match the Partner Center publisher identity." }
  & $SignTool.FullName verify /pa /v $Package
  if ($LASTEXITCODE -ne 0) { throw "Signature verification failed." }
} else {
  Write-Host "Created an unsigned Store submission package. Microsoft signs it after certification."
}

$Hash = Get-FileHash $Package -Algorithm SHA256
"$($Hash.Hash)  $([System.IO.Path]::GetFileName($Package))" |
  Set-Content (Join-Path $Artifacts "STORE-MSIX-SHA256.txt") -Encoding ascii

Write-Host "Store package: $Package"
Write-Host "Partner Center identity: SrSLogics.LakshyaAttendanceConnector"
Write-Host "Store ID: 9PHMJZRHP876"
