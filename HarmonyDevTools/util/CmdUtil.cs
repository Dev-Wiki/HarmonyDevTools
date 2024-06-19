using System;
using System.Diagnostics;
using System.Text;
using log4net;

namespace HarmonyDevTools.util;

public static class CmdUtil
{
    private static readonly ILog Log = LogManager.GetLogger(nameof(CmdUtil));
    private const string CmdExe = "cmd.exe";

    /**
     * 使用 cmd.exe 执行
     */
    public static string RunCmd(string parameter = "", bool withExit = true)
    {
        var output = new StringBuilder();
        try
        {
            var pro = new Process
            {
                StartInfo =
                {
                    FileName = CmdExe,
                    UseShellExecute = false,
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };
            if (parameter.Length > 0)
            {
                pro.StartInfo.Arguments = parameter;
            }

            pro.Start();

            if (parameter.Length > 0)
            {
                pro.StandardInput.WriteLine(parameter + (withExit ? " &exit" : ""));
                pro.StandardInput.AutoFlush = true;
            }
            
            while (!pro.StandardOutput.EndOfStream)
            {
                string? line = pro.StandardOutput.ReadLine();
                if (!string.IsNullOrEmpty(line) && !line.StartsWith("(c) Microsoft") && !line.StartsWith("Microsoft Windows"))
                {
                    output.AppendLine(line);
                }
            }

            if (withExit)
            {
                pro.WaitForExit();
                pro.Close();
            }
        }
        catch (Exception e)
        {
            Log.Error(e);
        }
        return output.ToString();
    }

    /**
     * 使用指定的 exe 文件执行
     */
    public static string RunExe(string exePath, string arguments = "")
    {
        var output = new StringBuilder();
        try
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = exePath,
                    Arguments = arguments,
                    UseShellExecute = false,
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };

            process.OutputDataReceived += (sender, args) =>
            {
                if (!string.IsNullOrEmpty(args.Data))
                {
                    output.AppendLine(args.Data);
                }
            };
                
            process.ErrorDataReceived += (sender, args) =>
            {
                if (!string.IsNullOrEmpty(args.Data))
                {
                    output.AppendLine($"ERROR: {args.Data}");
                }
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
                
            process.WaitForExit();
            process.Close();
        }
        catch (Exception e)
        {
            Log.Error(e);
        }
        return output.ToString();
    }
}