# Lakshya Attendance Connector for Windows

The connector runs on the Windows computer where eSSL saves attendance reports. It watches one folder for new **eSSL Form J PDF, XLS or XLSX** files and uploads them to Lakshya ERP over HTTPS. It is locked to `https://lakshyaedutech.onrender.com`; changing a local configuration file cannot redirect the operator's password or reports to another server.

## Operator workflow

1. Install the signed `Lakshya-Attendance-Connector-Setup.exe`.
2. Sign in with an active Attendance Desk account whose temporary password has already been changed.
3. Select the folder where eSSL saves Form J PDF or Excel reports.
4. Choose **Save and test connection**.
5. Keep exporting Form J PDF or Excel files into that folder. The connector starts with Windows and scans automatically.
6. The first report opens a one-time mapping screen for device codes. Map each code to the correct student or mark it **Ignore**.
7. Imported attendance appears as a **draft** Tatva/Essential register in Attendance Desk. Review it before submission.

The report file is used only during the short-lived secure preview and is never persisted to ERP database or object storage. Windows encrypts the connector password with DPAPI for the signed-in Windows user. Completed file hashes and file states are stored locally to avoid repeat uploads without repeatedly rereading old reports.

This release watches the eSSL export folder; it does not read fingerprint templates or connect directly to the X2008 device. Configure the existing eSSL software to save or export Form J PDF or Excel reports into the selected folder.

## Build

Requirements on Windows:

- .NET 8 SDK
- Windows 10/11 SDK (`SignTool`)
- Inno Setup 6
- A trusted code-signing certificate issued to the production publisher

Build and sign both the application and installer:

```powershell
.\build-installer.ps1 -CertificatePath C:\secure\publisher.pfx -CertificatePassword "<password>"
```

Never commit the PFX or its password. Use a timestamp server so signatures remain verifiable after certificate renewal.

The production command is intentionally strict: it requires a certificate, signs the application, builds the installer, signs the installer, verifies both signatures, and writes `artifacts\SHA256SUMS.txt`. Distribute only `artifacts\Lakshya-Attendance-Connector-Setup.exe` after the verification step succeeds.

## Microsoft Store MSIX

The Microsoft Partner Center product is reserved with these production values:

- Package identity: `SrSLogics.LakshyaAttendanceConnector`
- Publisher: `CN=9E014D47-CBFD-45BF-BE0E-DEA2D95C1B2E`
- Publisher display name: `SrS Logics`
- Store ID: `9PHMJZRHP876`

On a Windows build computer with the .NET 8 SDK and Windows 10/11 SDK installed, create the Store package with:

```powershell
.\build-store-msix.ps1 -Version 1.0.0.0
```

From GitHub, the same package can be produced without a local Windows build setup: open **Actions → Build attendance connector MSIX → Run workflow**, enter the four-part version, and download the resulting Store artifact.

Upload `artifacts\Lakshya-Attendance-Connector_1.0.0.0_x64.msix` to the reserved **Lakshya Attendance Connector** product in Partner Center. Microsoft signs an accepted MSIX during Store certification, so a commercial certificate is not required for the Store submission. A certificate whose subject exactly matches the Partner Center publisher identity is still required if the MSIX must be installed locally before Store certification.

The Store manifest enables startup after the first launch and passes `--background`, so the connector continues in the notification area without opening its setup window at every Windows sign-in. The operator remains able to disable it from Windows **Settings → Apps → Startup**.

## Windows trust and SmartScreen

The application requests `asInvoker` and installs per user, so it does not need administrator access for normal installation or operation. That alone does not establish publisher trust.

For external production distribution, sign the EXE and installer with a certificate that chains to a Windows-trusted certificate authority, or publish through Microsoft Store. A self-signed certificate is appropriate only for institute-managed computers after an administrator deliberately deploys its public certificate through the organization's Windows trust policy. Do not tell users to disable SmartScreen or antivirus protection, and do not distribute an unsigned development build.

New non-Store publishers can still receive a SmartScreen reputation warning until Microsoft has enough reputation for the signed publisher/download. Signing proves publisher identity and integrity; no application code can legitimately bypass that reputation system. Microsoft Store distribution provides the most predictable consumer installation experience; direct distribution requires an SRS Logics organization-validation code-signing certificate and may still need publisher reputation to accumulate.

Microsoft guidance:

- https://learn.microsoft.com/windows/msix/package/signing-package-overview
- https://learn.microsoft.com/windows/msix/package/sign-app-package-using-signtool
- https://learn.microsoft.com/windows/apps/package-and-deploy/choose-distribution-path
