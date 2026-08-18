using System.Security.Cryptography;

namespace Lakshya.Attendance.Connector;

internal sealed class ConnectorService : IDisposable
{
    private readonly ConnectorConfig _config;
    private readonly ErpApiClient _api;
    private readonly SemaphoreSlim _syncLock = new(1, 1);
    private readonly System.Threading.Timer _timer;
    private FileSystemWatcher? _watcher;
    private CancellationTokenSource _shutdown = new();
    private volatile bool _mappingPending;
    public event Action<string>? StatusChanged;
    public event Action<PreparedImport>? MappingRequired;

    public ConnectorService(ConnectorConfig config, ErpApiClient api)
    {
        _config = config;
        _api = api;
        _timer = new System.Threading.Timer(_ => _ = ScanAsync(false), null, Timeout.Infinite, Timeout.Infinite);
    }

    public void Start()
    {
        StopWatcher();
        Directory.CreateDirectory(_config.WatchFolder);
        _watcher = new FileSystemWatcher(_config.WatchFolder, "*.*")
        {
            IncludeSubdirectories = false,
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite | NotifyFilters.Size,
            EnableRaisingEvents = true
        };
        _watcher.Created += (_, _) => _ = ScanAsync(false);
        _watcher.Changed += (_, _) => _ = ScanAsync(false);
        _watcher.Renamed += (_, _) => _ = ScanAsync(false);
        _timer.Change(TimeSpan.FromSeconds(10), TimeSpan.FromMinutes(2));
        Emit($"Watching {_config.WatchFolder}");
    }

    public Task ScanNowAsync() => ScanAsync(true);

    private async Task ScanAsync(bool manual)
    {
        if (_mappingPending) return;
        if (!await _syncLock.WaitAsync(0)) return;
        try
        {
            var files = Directory.Exists(_config.WatchFolder)
                ? Directory.EnumerateFiles(_config.WatchFolder)
                    .Where(path => new[] { ".pdf", ".xls", ".xlsx" }.Contains(Path.GetExtension(path), StringComparer.OrdinalIgnoreCase))
                    .Select(path => new FileInfo(path))
                    .OrderBy(info => info.LastWriteTimeUtc)
                    .ToList()
                : [];
            if (files.Count == 0 && manual) Emit("No Form J PDF or Excel reports found in the selected folder.");
            foreach (var file in files)
            {
                var fileState = GetFileState(file);
                if (_config.CompletedFileStates.TryGetValue(file.FullName, out var completedState) && completedState == fileState)
                    continue;
                var fingerprint = await StableFingerprintAsync(file.FullName, _shutdown.Token);
                if (fingerprint is null) continue;
                if (_config.CompletedFiles.ContainsKey(fingerprint))
                {
                    MarkCompleted(fingerprint, file);
                    continue;
                }
                Emit($"Reading {file.Name}…");
                try
                {
                    var prepared = await _api.PrepareAsync(file.FullName, _shutdown.Token);
                    var unresolved = prepared.DeviceUsers.Where(item => string.IsNullOrWhiteSpace(item.StudentId) && !item.Ignore).ToList();
                    if (unresolved.Count > 0)
                    {
                        _mappingPending = true;
                        Emit($"{unresolved.Count} device IDs need one-time student mapping.");
                        MappingRequired?.Invoke(prepared);
                        return;
                    }
                    var mappings = prepared.DeviceUsers.Select(item => new MappingChoice(item.DeviceUserId, item.StudentId, item.Ignore)).ToList();
                    var message = await _api.CommitAsync(prepared, mappings, _shutdown.Token);
                    MarkCompleted(fingerprint, file);
                    Emit(message);
                }
                catch (ConnectorException error) when (error.StatusCode == System.Net.HttpStatusCode.Conflict && error.Message.Contains("already been imported", StringComparison.OrdinalIgnoreCase))
                {
                    MarkCompleted(fingerprint, file);
                    Emit($"Skipped {file.Name}; it was already imported.");
                }
                catch (Exception error) { Emit($"Sync paused: {error.Message}"); }
            }
        }
        finally { _syncLock.Release(); }
    }

    public async Task CompleteMappingAsync(PreparedImport prepared, IReadOnlyList<MappingChoice> choices)
    {
        try
        {
            var message = await _api.CommitAsync(prepared, choices, _shutdown.Token);
            var fingerprint = await StableFingerprintAsync(prepared.FilePath, _shutdown.Token);
            if (fingerprint is not null) MarkCompleted(fingerprint, new FileInfo(prepared.FilePath));
            Emit(message);
        }
        catch (ConnectorException error) when (error.StatusCode == System.Net.HttpStatusCode.Gone)
        {
            _mappingPending = false;
            Emit("The secure preview expired. Run Sync now and confirm the mappings again.");
        }
        finally { _mappingPending = false; }
    }

    public void CancelPendingMapping()
    {
        _mappingPending = false;
        Emit("Sync paused until the next scan; device mappings were not changed.");
    }

    private void MarkCompleted(string fingerprint, FileInfo file)
    {
        file.Refresh();
        _config.CompletedFiles[fingerprint] = $"{DateTimeOffset.UtcNow:O}|{file.Name}";
        _config.CompletedFileStates[file.FullName] = GetFileState(file);
        if (_config.CompletedFiles.Count > 500)
            foreach (var key in _config.CompletedFiles.Keys.Take(_config.CompletedFiles.Count - 500).ToList())
                _config.CompletedFiles.Remove(key);
        if (_config.CompletedFileStates.Count > 500)
            foreach (var key in _config.CompletedFileStates.Keys.Take(_config.CompletedFileStates.Count - 500).ToList())
                _config.CompletedFileStates.Remove(key);
        AppStorage.Save(_config);
    }

    private static string GetFileState(FileInfo file)
    {
        file.Refresh();
        return $"{file.Length}:{file.LastWriteTimeUtc.Ticks}";
    }

    private static async Task<string?> StableFingerprintAsync(string path, CancellationToken cancellationToken)
    {
        try
        {
            var first = new FileInfo(path);
            if (!first.Exists || first.Length == 0) return null;
            await Task.Delay(TimeSpan.FromSeconds(4), cancellationToken);
            var second = new FileInfo(path);
            if (!second.Exists || first.Length != second.Length || first.LastWriteTimeUtc != second.LastWriteTimeUtc) return null;
            await using var stream = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.Read);
            return Convert.ToHexString(await SHA256.HashDataAsync(stream, cancellationToken));
        }
        catch (IOException) { return null; }
    }

    private void Emit(string value) => StatusChanged?.Invoke($"{DateTime.Now:dd MMM, HH:mm} · {value}");
    private void StopWatcher() { _watcher?.Dispose(); _watcher = null; }
    public void Dispose()
    {
        _shutdown.Cancel();
        StopWatcher();
        _timer.Dispose();
        _syncLock.Dispose();
        _shutdown.Dispose();
    }
}
