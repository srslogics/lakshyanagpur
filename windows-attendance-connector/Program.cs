using System.Threading;

namespace Lakshya.Attendance.Connector;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        using var singleInstance = new Mutex(true, "Local\\SRSLogics.LakshyaAttendanceConnector", out var created);
        if (!created)
        {
            MessageBox.Show("Lakshya Attendance Connector is already running.", "Lakshya Attendance Connector");
            return;
        }
        ApplicationConfiguration.Initialize();
        Application.Run(new MainForm());
    }
}
