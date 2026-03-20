@echo off
echo 系统配置信息:
echo.
systeminfo | findstr /B /C:"OS 名称" /C:"系统制造商" /C:"系统型号" /C:"处理器" /C:"物理内存"
echo.
echo CPU详细信息:
wmic cpu get name
echo.
echo 内存详细信息:
wmic ComputerSystem get TotalPhysicalMemory
echo.
echo 磁盘信息:
wmic diskdrive get model,size
echo.
echo 显卡信息:
wmic path win32_VideoController get name
pause