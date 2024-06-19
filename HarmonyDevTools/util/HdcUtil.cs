using System;

namespace HarmonyDevTools.util;

public static class HdcUtil
{
    public static string ExportFile(string originPath)
    {
        var formattedDate = DateTime.Now.ToString("yyyy-MM-dd-HH-mm-ss");
        CmdUtil.RunCmd($"mkdir {formattedDate}");
        var command = $"file recv {originPath} ./{formattedDate}";
        return CmdUtil.RunExe("toolchains\\hdc.exe", command);
    }

    public static string RunCommand(string command)
    {
        return CmdUtil.RunExe("toolchains\\hdc.exe", command);
    }
}