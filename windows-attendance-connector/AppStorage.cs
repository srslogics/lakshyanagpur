using System.Security.Cryptography;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using Microsoft.Win32;

namespace Lakshya.Attendance.Connector;

internal sealed class ConnectorConfig
{
    public string ServerUrl { get; set; } = "https://lakshyaedutech.onrender.com";
    public string WatchFolder { get; set; } = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
    public string Mobile { get; set; } = "";
    public bool StartWithWindows { get; set; } = true;
    public Dictionary<string, string> CompletedFiles { get; set; } = new();
    public Dictionary<string, string> CompletedFileStates { get; set; } = new(StringComparer.OrdinalIgnoreCase);
}

internal static class AppStorage
{
    private const int ErrorSuccess = 0;
    private const int ErrorInsufficientBuffer = 122;
    private static readonly string Root = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "SRS Logics", "Lakshya Attendance Connector");
    private static readonly string ConfigPath = Path.Combine(Root, "connector.json");
    private static readonly string SecretPath = Path.Combine(Root, "credentials.bin");
    private static readonly byte[] Entropy = Encoding.UTF8.GetBytes("SRSLogics.LakshyaAttendanceConnector.v1");

    public static bool IsPackaged
    {
        get
        {
            var length = 0;
            var result = GetCurrentPackageFullName(ref length, null);
            return result is ErrorSuccess or ErrorInsufficientBuffer;
        }
    }

    public static ConnectorConfig Load()
    {
        Directory.CreateDirectory(Root);
        try
        {
            return File.Exists(ConfigPath)
                ? JsonSerializer.Deserialize<ConnectorConfig>(File.ReadAllText(ConfigPath)) ?? new ConnectorConfig()
                : new ConnectorConfig();
        }
        catch { return new ConnectorConfig(); }
    }

    public static void Save(ConnectorConfig config)
    {
        Directory.CreateDirectory(Root);
        File.WriteAllText(ConfigPath, JsonSerializer.Serialize(config, new JsonSerializerOptions { WriteIndented = true }));
    }

    public static void SavePassword(string password)
    {
        Directory.CreateDirectory(Root);
        var clear = Encoding.UTF8.GetBytes(password);
        var protectedBytes = ProtectedData.Protect(clear, Entropy, DataProtectionScope.CurrentUser);
        File.WriteAllBytes(SecretPath, protectedBytes);
        CryptographicOperations.ZeroMemory(clear);
    }

    public static string LoadPassword()
    {
        if (!File.Exists(SecretPath)) return "";
        try
        {
            var clear = ProtectedData.Unprotect(File.ReadAllBytes(SecretPath), Entropy, DataProtectionScope.CurrentUser);
            try { return Encoding.UTF8.GetString(clear); }
            finally { CryptographicOperations.ZeroMemory(clear); }
        }
        catch { return ""; }
    }

    public static void SetStartup(bool enabled)
    {
        // Store-installed builds use the startup task declared in AppxManifest.xml.
        // A Run-key entry would contain a versioned WindowsApps path and break after an update.
        if (IsPackaged) return;

        using var key = Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run");
        const string name = "Lakshya Attendance Connector";
        if (enabled)
            key?.SetValue(name, $"\"{Application.ExecutablePath}\" --background");
        else
            key?.DeleteValue(name, false);
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern int GetCurrentPackageFullName(
        ref int packageFullNameLength,
        StringBuilder? packageFullName);
}
