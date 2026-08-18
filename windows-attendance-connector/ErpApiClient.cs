using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Lakshya.Attendance.Connector;

internal sealed record StudentOption(string Id, string AdmissionNumber, string FullName, string? Batch);
internal sealed record DeviceUser(string DeviceUserId, string DeviceName, int DayCount, string? StudentId, bool Ignore);
internal sealed record MappingChoice(string DeviceUserId, string? StudentId, bool Ignore);
internal sealed record PreparedImport(
    string FilePath,
    string PreviewToken,
    string SheetName,
    IReadOnlyList<StudentOption> Students,
    IReadOnlyList<DeviceUser> DeviceUsers,
    int RowsSeen,
    string DateFrom,
    string DateTo);

internal sealed class ErpApiClient : IDisposable
{
    private const string ProductionHost = "lakshyaedutech.onrender.com";
    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromMinutes(2) };
    private string _serverUrl = "";
    private string _mobile = "";
    private string _password = "";
    private string? _token;
    private DateTimeOffset _tokenExpiresAt;

    public void Configure(string serverUrl, string mobile, string password)
    {
        if (!Uri.TryCreate(serverUrl.Trim(), UriKind.Absolute, out var server) ||
            server.Scheme != Uri.UriSchemeHttps ||
            !server.Host.Equals(ProductionHost, StringComparison.OrdinalIgnoreCase))
            throw new ConnectorException("The connector can only pair with the official Lakshya ERP address.");
        _serverUrl = $"{server.Scheme}://{server.Authority}";
        _mobile = new string(mobile.Where(char.IsDigit).ToArray());
        if (_mobile.Length > 10) _mobile = _mobile[^10..];
        _password = password;
        _token = null;
    }

    public async Task VerifyAsync(CancellationToken cancellationToken) => await AuthenticateAsync(cancellationToken);

    public async Task<PreparedImport> PrepareAsync(string filePath, CancellationToken cancellationToken)
    {
        await EnsureAuthenticatedAsync(cancellationToken);
        using var form = new MultipartFormDataContent();
        await using var stream = File.Open(filePath, FileMode.Open, FileAccess.Read, FileShare.Read);
        var file = new StreamContent(stream);
        file.Headers.ContentType = new MediaTypeHeaderValue(Path.GetExtension(filePath).ToLowerInvariant() switch
        {
            ".pdf" => "application/pdf",
            ".xls" => "application/vnd.ms-excel",
            ".xlsx" => "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            _ => "application/octet-stream"
        });
        form.Add(file, "file", Path.GetFileName(filePath));
        using var previewResponse = await SendAsync(HttpMethod.Post, "/api/attendance/biometric-imports/preview", form, cancellationToken);
        var preview = await ReadJsonAsync<PreviewResponse>(previewResponse, cancellationToken);
        if (!preview.SourceFormat.StartsWith("essl_form_j", StringComparison.Ordinal))
            throw new ConnectorException("Only eSSL Form J PDF or Excel reports are synchronized automatically.");
        var sheetName = preview.Sheets.FirstOrDefault()?.Name ?? throw new ConnectorException("The file has no attendance report.");
        var selection = Selection(preview.PreviewToken, sheetName);
        using var analysisResponse = await SendJsonAsync(HttpMethod.Post, "/api/attendance/biometric-imports/analyze", selection, cancellationToken);
        var analysis = await ReadJsonAsync<AnalysisResponse>(analysisResponse, cancellationToken);
        return new PreparedImport(filePath, preview.PreviewToken, sheetName, preview.Students, analysis.DeviceUsers,
            analysis.RowsSeen, analysis.DateFrom, analysis.DateTo);
    }

    public async Task<string> CommitAsync(PreparedImport prepared, IReadOnlyList<MappingChoice> mappings, CancellationToken cancellationToken)
    {
        await EnsureAuthenticatedAsync(cancellationToken);
        var payload = new
        {
            previewToken = prepared.PreviewToken,
            sheetName = prepared.SheetName,
            deviceIdColumn = "Device Code",
            nameColumn = "Student Name",
            datetimeColumn = (string?)null,
            dateColumn = "Date",
            timeColumn = "InTime",
            mappings = mappings.Select(item => new { deviceUserId = item.DeviceUserId, studentId = item.StudentId, ignore = item.Ignore })
        };
        using var response = await SendJsonAsync(HttpMethod.Post, "/api/attendance/biometric-imports", payload, cancellationToken);
        var body = await ReadJsonAsync<CommitResponse>(response, cancellationToken);
        return body.Message;
    }

    private object Selection(string token, string sheetName) => new
    {
        previewToken = token,
        sheetName,
        deviceIdColumn = "Device Code",
        nameColumn = "Student Name",
        datetimeColumn = (string?)null,
        dateColumn = "Date",
        timeColumn = "InTime"
    };

    private async Task AuthenticateAsync(CancellationToken cancellationToken)
    {
        using var response = await _http.PostAsJsonAsync($"{_serverUrl}/api/auth/login", new { mobile = _mobile, password = _password }, cancellationToken);
        var result = await ReadJsonAsync<LoginResponse>(response, cancellationToken);
        if (result.User.Role is not ("attendance_operator" or "academic_coordinator" or "owner"))
            throw new ConnectorException("This account is not permitted to synchronize attendance.");
        if (result.User.MustChangePassword)
            throw new ConnectorException("Change the temporary password in Attendance Desk before pairing this connector.");
        _token = result.AccessToken;
        _tokenExpiresAt = DateTimeOffset.UtcNow.AddSeconds(Math.Max(60, result.ExpiresIn - 60));
    }

    private async Task EnsureAuthenticatedAsync(CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(_token) || DateTimeOffset.UtcNow >= _tokenExpiresAt)
            await AuthenticateAsync(cancellationToken);
    }

    private async Task<HttpResponseMessage> SendJsonAsync(HttpMethod method, string path, object payload, CancellationToken cancellationToken)
    {
        var request = new HttpRequestMessage(method, $"{_serverUrl}{path}") { Content = JsonContent.Create(payload) };
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _token);
        return await _http.SendAsync(request, cancellationToken);
    }

    private async Task<HttpResponseMessage> SendAsync(HttpMethod method, string path, HttpContent content, CancellationToken cancellationToken)
    {
        var request = new HttpRequestMessage(method, $"{_serverUrl}{path}") { Content = content };
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _token);
        return await _http.SendAsync(request, cancellationToken);
    }

    private static async Task<T> ReadJsonAsync<T>(HttpResponseMessage response, CancellationToken cancellationToken)
    {
        var text = await response.Content.ReadAsStringAsync(cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            var message = text;
            try
            {
                using var json = JsonDocument.Parse(text);
                var detail = json.RootElement.GetProperty("detail");
                message = detail.ValueKind == JsonValueKind.String
                    ? detail.GetString() ?? text
                    : detail.TryGetProperty("message", out var nested) ? nested.GetString() ?? text : text;
            }
            catch { }
            throw new ConnectorException(message, response.StatusCode);
        }
        return JsonSerializer.Deserialize<T>(text, JsonOptions) ?? throw new ConnectorException("The ERP returned an empty response.");
    }

    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true };
    public void Dispose() => _http.Dispose();

    private sealed record LoginResponse(
        [property: JsonPropertyName("access_token")] string AccessToken,
        [property: JsonPropertyName("expires_in")] int ExpiresIn,
        LoginUser User);
    private sealed record LoginUser(string Role, bool MustChangePassword);
    private sealed record PreviewResponse(string PreviewToken, string SourceFormat, List<StudentOption> Students, List<PreviewSheet> Sheets);
    private sealed record PreviewSheet(string Name);
    private sealed record AnalysisResponse(int RowsSeen, string DateFrom, string DateTo, List<DeviceUser> DeviceUsers);
    private sealed record CommitResponse(string Message);
}

internal sealed class ConnectorException : Exception
{
    public HttpStatusCode? StatusCode { get; }
    public ConnectorException(string message, HttpStatusCode? statusCode = null) : base(message) => StatusCode = statusCode;
}
