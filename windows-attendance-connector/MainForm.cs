using System.Diagnostics;

namespace Lakshya.Attendance.Connector;

internal sealed class MainForm : Form
{
    private const string OfficialErpUrl = "https://lakshyaedutech.onrender.com";
    private readonly ConnectorConfig _config = AppStorage.Load();
    private readonly ErpApiClient _api = new();
    private ConnectorService? _service;
    private readonly TextBox _server = new() { Dock = DockStyle.Fill, ReadOnly = true };
    private readonly TextBox _folder = new() { Dock = DockStyle.Fill, ReadOnly = true };
    private readonly TextBox _mobile = new() { Dock = DockStyle.Fill, PlaceholderText = "10-digit mobile number" };
    private readonly TextBox _password = new() { Dock = DockStyle.Fill, UseSystemPasswordChar = true, PlaceholderText = "Attendance Desk password" };
    private readonly CheckBox _startup = new() { Text = "Start automatically when Windows starts", AutoSize = true };
    private readonly Label _status = new() { Dock = DockStyle.Fill, AutoSize = true, ForeColor = Color.FromArgb(39, 45, 112) };
    private readonly Button _save = new() { Text = "Save and test connection", AutoSize = true, Height = 42 };
    private readonly Button _scan = new() { Text = "Sync now", AutoSize = true, Height = 42, Enabled = false };
    private readonly NotifyIcon _tray = new() { Text = "Lakshya Attendance Connector", Visible = true, Icon = SystemIcons.Information };
    private bool _allowClose;
    private bool _mappingDialogOpen;

    public MainForm()
    {
        _config.ServerUrl = OfficialErpUrl;
        Text = "Lakshya Attendance Connector";
        ClientSize = new Size(680, 480);
        MinimumSize = new Size(620, 440);
        StartPosition = FormStartPosition.CenterScreen;
        Font = new Font("Segoe UI", 10);
        BackColor = Color.FromArgb(248, 247, 242);
        Icon = SystemIcons.Information;
        BuildInterface();
        Load += async (_, _) => await StartConfiguredAsync();
        FormClosing += OnFormClosing;
        _tray.DoubleClick += (_, _) => RestoreWindow();
        _tray.ContextMenuStrip = BuildTrayMenu();
    }

    private void BuildInterface()
    {
        var outer = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(30), RowCount = 6, ColumnCount = 1 };
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        outer.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));

        var title = new Label { Text = "Lakshya Attendance Connector", AutoSize = true, Font = new Font("Segoe UI", 22, FontStyle.Bold), ForeColor = Color.FromArgb(20, 22, 56), Margin = new Padding(0, 0, 0, 7) };
        var intro = new Label { Text = "Securely watches the eSSL report folder and transfers new Form J attendance PDFs to Lakshya ERP as draft registers.", AutoSize = true, MaximumSize = new Size(610, 0), ForeColor = Color.FromArgb(95, 96, 110), Margin = new Padding(0, 0, 0, 22) };
        outer.Controls.Add(title);
        outer.Controls.Add(intro);

        var form = new TableLayoutPanel { Dock = DockStyle.Top, ColumnCount = 3, RowCount = 4, AutoSize = true };
        form.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 145));
        form.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        form.ColumnStyles.Add(new ColumnStyle(SizeType.AutoSize));
        AddRow(form, 0, "ERP address", _server);
        var browse = new Button { Text = "Choose folder", AutoSize = true, Height = 32 };
        browse.Click += (_, _) => ChooseFolder();
        AddRow(form, 1, "eSSL export folder", _folder, browse);
        AddRow(form, 2, "Mobile number", _mobile);
        AddRow(form, 3, "Password", _password);
        outer.Controls.Add(form);

        _startup.Margin = new Padding(148, 15, 0, 0);
        outer.Controls.Add(_startup);
        var statusCard = new Panel { Dock = DockStyle.Fill, Padding = new Padding(18), Margin = new Padding(0, 22, 0, 18), BackColor = Color.White, BorderStyle = BorderStyle.FixedSingle };
        statusCard.Controls.Add(_status);
        outer.Controls.Add(statusCard);
        var actions = new FlowLayoutPanel { Dock = DockStyle.Bottom, FlowDirection = FlowDirection.RightToLeft, AutoSize = true };
        actions.Controls.Add(_save);
        actions.Controls.Add(_scan);
        outer.Controls.Add(actions);
        Controls.Add(outer);

        _server.Text = OfficialErpUrl;
        _folder.Text = _config.WatchFolder;
        _mobile.Text = _config.Mobile;
        _password.Text = AppStorage.LoadPassword();
        _startup.Checked = _config.StartWithWindows;
        _status.Text = "Complete the setup, then choose Save and test connection.";
        _save.Click += async (_, _) => await SaveAsync();
        _scan.Click += async (_, _) => { if (_service is not null) await _service.ScanNowAsync(); };
    }

    private static void AddRow(TableLayoutPanel table, int row, string label, Control control, Control? action = null)
    {
        table.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        table.Controls.Add(new Label { Text = label, AutoSize = true, Anchor = AnchorStyles.Left, Font = new Font("Segoe UI", 9, FontStyle.Bold), Margin = new Padding(0, 10, 10, 10) }, 0, row);
        control.Margin = new Padding(0, 5, 8, 5);
        table.Controls.Add(control, 1, row);
        if (action is not null) { action.Margin = new Padding(0, 5, 0, 5); table.Controls.Add(action, 2, row); }
    }

    private async Task SaveAsync()
    {
        _save.Enabled = false;
        SetStatus("Testing the secure ERP connection…");
        try
        {
            if (!Directory.Exists(_folder.Text)) throw new ConnectorException("Choose a folder that exists on this computer.");
            _api.Configure(_server.Text, _mobile.Text, _password.Text);
            await _api.VerifyAsync(CancellationToken.None);
            _config.ServerUrl = OfficialErpUrl;
            _config.WatchFolder = _folder.Text;
            _config.Mobile = new string(_mobile.Text.Where(char.IsDigit).ToArray());
            if (_config.Mobile.Length > 10) _config.Mobile = _config.Mobile[^10..];
            _config.StartWithWindows = _startup.Checked;
            AppStorage.SavePassword(_password.Text);
            AppStorage.Save(_config);
            AppStorage.SetStartup(_config.StartWithWindows);
            StartService();
            SetStatus("Connected. New eSSL Form J PDFs will synchronize automatically.");
        }
        catch (Exception error) { SetStatus($"Setup needs attention: {error.Message}"); }
        finally { _save.Enabled = true; }
    }

    private async Task StartConfiguredAsync()
    {
        if (string.IsNullOrWhiteSpace(_config.Mobile) || string.IsNullOrWhiteSpace(AppStorage.LoadPassword())) return;
        _api.Configure(_config.ServerUrl, _config.Mobile, AppStorage.LoadPassword());
        try
        {
            await _api.VerifyAsync(CancellationToken.None);
            StartService();
            SetStatus("Connected. Watching for new eSSL attendance reports.");
            if (Environment.GetCommandLineArgs().Contains("--background")) Hide();
        }
        catch (Exception error) { SetStatus($"Connection needs attention: {error.Message}"); }
    }

    private void StartService()
    {
        _service?.Dispose();
        _service = new ConnectorService(_config, _api);
        _service.StatusChanged += message => BeginInvoke(new Action(() => SetStatus(message)));
        _service.MappingRequired += prepared => BeginInvoke(new Action(() => OpenMapping(prepared)));
        _service.Start();
        _scan.Enabled = true;
    }

    private void ChooseFolder()
    {
        using var dialog = new FolderBrowserDialog { Description = "Choose the folder where eSSL saves Form J PDF reports", UseDescriptionForTitle = true, ShowNewFolderButton = true, SelectedPath = _folder.Text };
        if (dialog.ShowDialog(this) == DialogResult.OK) _folder.Text = dialog.SelectedPath;
    }

    private void OpenMapping(PreparedImport prepared)
    {
        if (_mappingDialogOpen) return;
        _mappingDialogOpen = true;
        RestoreWindow();
        using var dialog = new MappingForm(prepared);
        var result = dialog.ShowDialog(this);
        _mappingDialogOpen = false;
        if (result != DialogResult.OK || _service is null)
        {
            _service?.CancelPendingMapping();
            return;
        }
        _ = CompleteMappingAsync(prepared, dialog.Choices);
    }

    private async Task CompleteMappingAsync(PreparedImport prepared, IReadOnlyList<MappingChoice> choices)
    {
        try { if (_service is not null) await _service.CompleteMappingAsync(prepared, choices); }
        catch (Exception error) { SetStatus($"Mapping was not saved: {error.Message}"); }
    }

    private ContextMenuStrip BuildTrayMenu()
    {
        var menu = new ContextMenuStrip();
        menu.Items.Add("Open connector", null, (_, _) => RestoreWindow());
        menu.Items.Add("Sync now", null, async (_, _) => { if (_service is not null) await _service.ScanNowAsync(); });
        menu.Items.Add("Open Attendance Desk", null, (_, _) => Process.Start(new ProcessStartInfo($"{_config.ServerUrl}/attendance-app/") { UseShellExecute = true }));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add("Exit", null, (_, _) => { _allowClose = true; Close(); });
        return menu;
    }

    private void RestoreWindow() { Show(); WindowState = FormWindowState.Normal; Activate(); }
    private void OnFormClosing(object? sender, FormClosingEventArgs args)
    {
        if (_allowClose) { _tray.Visible = false; _service?.Dispose(); _api.Dispose(); return; }
        args.Cancel = true;
        Hide();
        _tray.ShowBalloonTip(2500, "Lakshya Attendance Connector", "The connector is still running securely in the notification area.", ToolTipIcon.Info);
    }
    private void SetStatus(string value) { _status.Text = value; _tray.Text = value.Length > 63 ? value[..63] : value; }
}
