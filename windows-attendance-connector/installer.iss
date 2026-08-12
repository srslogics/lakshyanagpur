#define MyAppName "Lakshya Attendance Connector"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SRS Logics"
#define MyAppURL "https://srslogics.com"
#define MyAppExeName "LakshyaAttendanceConnector.exe"

[Setup]
AppId={{F0D91665-C42F-4CBB-AF7E-BF88622918D0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\Lakshya Attendance Connector
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=artifacts
OutputBaseFilename=Lakshya-Attendance-Connector-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Files]
Source: "artifacts\Lakshya-Attendance-Connector\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Open {#MyAppName}"; Flags: nowait postinstall skipifsilent
