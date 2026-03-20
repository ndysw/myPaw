@echo off
echo 正在获取系统配置信息...
echo.
echo ===== 系统信息 =====
systeminfo | findstr /B /C:"主机名" /C:"OS 名称" /C:"OS 版本" /C:"系统制造商" /C:"系统型号" /C:"系统类型" /C:"处理器" /C:"物理内存"
echo.
echo ===== CPU 信息 =====
wmic cpu get name,NumberOfCores,NumberOfLogicalProcessors
wmic cpu get MaxClockSpeed
wmic cpu get L2CacheSize,L3CacheSize
echo.
echo ===== 内存信息 =====
wmic memorychip get Capacity,Speed,MemoryType,FormFactor
echo.
echo ===== 磁盘信息 =====
wmic diskdrive get model,size,interfaceType
echo.
echo ===== 显卡信息 =====
wmic path win32_VideoController get name,AdapterRAM,DriverVersion
echo.
echo ===== 网络适配器 =====
wmic nicconfig where IPEnabled=true get description,IPAddress
echo.
echo 系统信息获取完成!
pause