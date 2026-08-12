namespace Lakshya.Attendance.Connector;

internal sealed class MappingForm : Form
{
    private readonly PreparedImport _prepared;
    private readonly List<(DeviceUser User, ComboBox Student, CheckBox Ignore)> _rows = [];
    public IReadOnlyList<MappingChoice> Choices { get; private set; } = [];

    public MappingForm(PreparedImport prepared)
    {
        _prepared = prepared;
        Text = "Map biometric IDs to students";
        ClientSize = new Size(900, 620);
        MinimumSize = new Size(760, 500);
        StartPosition = FormStartPosition.CenterParent;
        Font = new Font("Segoe UI", 9);
        BuildInterface();
    }

    private void BuildInterface()
    {
        var outer = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(22), RowCount = 3 };
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        outer.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        outer.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        outer.Controls.Add(new Label
        {
            Text = $"{Path.GetFileName(_prepared.FilePath)} · {_prepared.RowsSeen} first punches · {_prepared.DateFrom} to {_prepared.DateTo}\nChoose the correct student for every new device ID. The ERP remembers these mappings for future reports.",
            AutoSize = true, MaximumSize = new Size(820, 0), Margin = new Padding(0, 0, 0, 14)
        });
        var grid = new TableLayoutPanel { Dock = DockStyle.Fill, AutoScroll = true, ColumnCount = 3, Padding = new Padding(0, 0, 10, 0) };
        grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 32));
        grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));
        grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 18));
        var studentSource = _prepared.Students.OrderBy(item => item.FullName).ToList();
        foreach (var user in _prepared.DeviceUsers)
        {
            var row = grid.RowCount++;
            grid.RowStyles.Add(new RowStyle(SizeType.AutoSize));
            var identity = new Label { Text = $"{user.DeviceUserId}  ·  {user.DeviceName}\n{user.DayCount} attendance day(s)", AutoSize = true, Margin = new Padding(0, 10, 8, 10) };
            var student = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Dock = DockStyle.Top, Margin = new Padding(0, 7, 8, 7) };
            student.Items.Add(new StudentChoice(null, "Choose student"));
            foreach (var item in studentSource)
                student.Items.Add(new StudentChoice(item.Id, $"{item.FullName} · {item.AdmissionNumber} · {item.Batch}"));
            student.SelectedIndex = 0;
            if (!string.IsNullOrWhiteSpace(user.StudentId))
                student.SelectedItem = student.Items.Cast<StudentChoice>().FirstOrDefault(item => item.Id == user.StudentId) ?? student.Items[0];
            var ignore = new CheckBox { Text = "Ignore", Checked = user.Ignore, AutoSize = true, Margin = new Padding(8, 11, 0, 8) };
            student.Enabled = !ignore.Checked;
            ignore.CheckedChanged += (_, _) => { student.Enabled = !ignore.Checked; if (ignore.Checked) student.SelectedIndex = 0; };
            student.SelectedIndexChanged += (_, _) => { if (((StudentChoice)student.SelectedItem!).Id is not null) ignore.Checked = false; };
            grid.Controls.Add(identity, 0, row); grid.Controls.Add(student, 1, row); grid.Controls.Add(ignore, 2, row);
            _rows.Add((user, student, ignore));
        }
        outer.Controls.Add(grid);
        var footer = new FlowLayoutPanel { Dock = DockStyle.Bottom, FlowDirection = FlowDirection.RightToLeft, AutoSize = true, Margin = new Padding(0, 14, 0, 0) };
        var import = new Button { Text = "Save mappings and import", AutoSize = true, Height = 40 };
        var cancel = new Button { Text = "Cancel", AutoSize = true, Height = 40, DialogResult = DialogResult.Cancel };
        import.Click += (_, _) => SaveMappings();
        footer.Controls.Add(import); footer.Controls.Add(cancel); outer.Controls.Add(footer);
        Controls.Add(outer);
        AcceptButton = import; CancelButton = cancel;
    }

    private void SaveMappings()
    {
        var choices = new List<MappingChoice>();
        foreach (var (user, student, ignore) in _rows)
        {
            var selected = (StudentChoice)student.SelectedItem!;
            if (selected.Id is null && !ignore.Checked)
            {
                MessageBox.Show($"Choose a student or Ignore device ID {user.DeviceUserId}.", "Mapping required", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                student.Focus(); return;
            }
            choices.Add(new MappingChoice(user.DeviceUserId, selected.Id, ignore.Checked));
        }
        var duplicates = choices.Where(item => item.StudentId is not null).GroupBy(item => item.StudentId).FirstOrDefault(group => group.Count() > 1);
        if (duplicates is not null)
        {
            MessageBox.Show("One student cannot be assigned to two device IDs.", "Duplicate mapping", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }
        Choices = choices; DialogResult = DialogResult.OK; Close();
    }

    private sealed record StudentChoice(string? Id, string Label) { public override string ToString() => Label; }
}
