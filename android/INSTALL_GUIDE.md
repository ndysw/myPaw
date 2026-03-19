# myPAW Android 应用安装和测试指南

## 📱 APK 文件信息

- **文件路径**: `app/build/outputs/apk/release/app-release.apk`
- **文件大小**: 4.9 MB
- **构建时间**: 2026-03-19 12:37
- **包名**: com.mypaw
- **版本**: 1.0 (versionCode: 1)

## 🚀 安装步骤

### 1. 连接 Android 设备

确保你的 Android 设备已连接到电脑，并开启 USB 调试：

```bash
# 检查设备连接
adb devices

# 如果没有设备，尝试以下命令：
adb kill-server
adb start-server
```

### 2. 卸载旧版本（如果已安装）

```bash
adb uninstall com.mypaw
```

### 3. 安装新版本

```bash
# 从项目目录安装
adb install "app/build/outputs/apk/release/app-release.apk"

# 或者从完整路径安装
adb install "D:\AI\myPAW\android\app\build\outputs\apk\release\app-release.apk"
```

### 4. 启动应用

```bash
# 启动应用
adb shell am start -n com.mypaw/.MainActivity

# 或者手动在设备上点击应用图标
```

## 🔍 故障排除

### 如果应用闪退

获取错误日志：

```bash
# 实时查看日志
adb logcat

# 或者保存到文件后分析
adb logcat -d > crash_log.txt

# 过滤 myPAW 相关日志
adb logcat | grep myPAW

# 查看崩溃信息
adb logcat | grep -E "AndroidRuntime|FATAL|Exception"
```

### 如果出现 "Binary XML" 错误

这通常表示资源文件有问题。检查：

1. **主题兼容性** - 已修复为 Material Components
2. **布局文件** - 确保所有引用的资源都存在
3. **drawable 资源** - 检查 XML 格式是否正确

### 如果无法连接到桌面端

1. **检查桌面端服务器**：
   ```bash
   # 确保桌面端 Flask 服务器运行
   python main_desktop.py
   ```

2. **检查网络连接**：
   - 确保手机和电脑在同一局域网
   - 尝试 ping 电脑 IP 地址

3. **配置服务器地址**：
   - 打开 myPAW 应用
   - 点击菜单 → "服务器设置"
   - 输入正确的桌面端 IP 地址（格式：`http://192.168.1.xxx:8000/`）

## 📋 应用功能

### 主要功能

1. **聊天界面** - 发送指令到桌面端
2. **语音输入** - 通过语音识别发送指令
3. **快速操作** - 预设常用指令
4. **服务器设置** - 配置桌面端连接地址

### 支持的指令

通过桌面端 LLM 引擎，支持以下指令：

- **文件操作**: 查看、读取、修改、删除文件
- **编译运行**: 执行 Python、Java 等代码
- **浏览器操作**: 访问网页、截图、提取内容
- **系统控制**: 启动应用、调节音量等

## 🎯 测试步骤

1. **启动应用** - 检查是否正常显示界面
2. **配置服务器** - 设置桌面端 IP 地址
3. **发送测试指令** - 如 "查看当前目录"
4. **检查响应** - 确认桌面端正确响应

## 📞 技术支持

如果遇到问题，请提供：

1. **错误日志** - `adb logcat` 输出
2. **设备信息** - Android 版本、型号
3. **网络环境** - 局域网 IP 地址
4. **桌面端状态** - Flask 服务器是否运行

---

**构建完成时间**: 2026-03-19 12:37
**主题修复**: Material Components DayNight
**签名状态**: ✅ 已签名