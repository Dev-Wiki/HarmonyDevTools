using System;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows;
using HarmonyDevTools.util;
using Microsoft.Win32;

namespace HarmonyDevTools;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    private void InstallOnClick(object sender, RoutedEventArgs e)
    {
        OpenFileDialog dialog = new OpenFileDialog() 
        {
            Title = "Select a package",
            Filter = "HarmonyNEXT(*.hap)|*.hap",
            FilterIndex = 1,
            RestoreDirectory = true
        };
        if (dialog.ShowDialog() == true)
        {
            // 获取所选文件的路径并显示在文本框中
            string filePath = dialog.FileName;
            AppendHintAndScrollToEnd($"select file: {filePath} \n");
            string command = "install";
            if (ReplaceCb.IsChecked ?? false)
            {
                command += " -r";
            }

            if (DowngradeCb.IsChecked ?? false)
            {
                command += " -d";
            }

            if (DynamicCb.IsChecked ?? false)
            {
                command += " -g";
            }
            CommandTb.Text = $"{command} {filePath}";
            GetCommandAndExecute();
        }
    }

    private void CommandBtn_OnClick(object sender, RoutedEventArgs e)
    {
        GetCommandAndExecute();
    }

    private void ListBtn_OnClick(object sender, RoutedEventArgs e)
    {
        CommandTb.Text = "list targets -v";
        GetCommandAndExecute();
    }

    private async void GetCommandAndExecute()
    {
        string command = CommandTb.Text;
        AppendHintAndScrollToEnd( $"execute command: {command} \n");
        string result = await Task.Run(() => HdcUtil.RunCommand(command));
        AppendHintAndScrollToEnd($"execute result: {result} \n");
    }
    
    private void CheckServerBtn_OnClick(object sender, RoutedEventArgs e)
    {
        CommandTb.Text = "checkserver";
        GetCommandAndExecute();
    }

    private void ConnectBtn_OnClick(object sender, RoutedEventArgs e)
    {
        CommandTb.Text = $"-t {TargetTb.Text}";
        GetCommandAndExecute();
    }

    private void KillBtn_OnClick(object sender, RoutedEventArgs e)
    {
        CommandTb.Text = "kill -r";
        GetCommandAndExecute();
    }

    protected override void OnClosing(CancelEventArgs e)
    {
        e.Cancel = true;
        KillHdcExe();
        e.Cancel = false;
    }

    private async void KillHdcExe()
    {
        string result = await Task.Run(() => CmdUtil.RunCmd("taskkill /IM hdc.exe"));
        AppendHintAndScrollToEnd(result + "\n");
    }

    private void UninstallBtn_OnClick(object sender, RoutedEventArgs e)
    {
        CommandTb.Text = $"uninstall {PackageNameTb.Text}";
        GetCommandAndExecute();
    }

    private void AppendHintAndScrollToEnd(string hint)
    {
        ResultTb.Text += hint;
        ResultTb.ScrollToEnd();
    }

    private void GetImage_OnClick(object sender, RoutedEventArgs e)
    {
        ExportFile("/storage/media/100/local/files/Photo");
    }

    private async void ExportFile(string path)
    {
        var formattedDate = DateTime.Now.ToString("yyyy-MM-dd-HH-mm-ss");
        CmdUtil.RunCmd($"mkdir {formattedDate}");
        AppendHintAndScrollToEnd($"create dir: {formattedDate} \n");
        AppendHintAndScrollToEnd($"export {path} to {formattedDate} \n");
        string result = await Task.Run(() => HdcUtil.ExportFile(path));
        AppendHintAndScrollToEnd($"export result: {result} \n");
    }
}