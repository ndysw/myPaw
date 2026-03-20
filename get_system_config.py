import platform
import psutil
import os

def get_system_info():
    print("=== 电脑配置信息 ===")
    print()
    
    # 系统信息
    print("系统信息:")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"系统版本: {platform.version()}")
    print(f"系统架构: {platform.architecture()[0]}")
    print(f"机器类型: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    print()
    
    # CPU信息
    print("CPU信息:")
    print(f"CPU核心数: {psutil.cpu_count(logical=False)} (物理核心)")
    print(f"CPU线程数: {psutil.cpu_count(logical=True)} (逻辑核心)")
    print(f"CPU使用率: {psutil.cpu_percent(interval=1)}%")
    print()
    
    # 内存信息
    print("内存信息:")
    memory = psutil.virtual_memory()
    print(f"总内存: {memory.total / (1024**3):.2f} GB")
    print(f"可用内存: {memory.available / (1024**3):.2f} GB")
    print(f"内存使用率: {memory.percent}%")
    print()
    
    # 磁盘信息
    print("磁盘信息:")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"磁盘 {partition.device}: {usage.total / (1024**3):.2f} GB (使用率: {usage.percent}%)")
        except PermissionError:
            continue
    print()
    
    # 网络信息
    print("网络信息:")
    try:
        addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in addrs.items():
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    print(f"{interface_name}: {address.address}")
    except:
        print("无法获取网络信息")

if __name__ == "__main__":
    get_system_info()