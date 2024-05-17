import os
import subprocess
import ctypes
import sys
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Re-run the script with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

def run_command(command):
    subprocess.run(command, shell=True)

password = "RVNCpass"
exe_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "bin")

def install_service():
    try:
        # 检查服务是否存在并正在运行
        result = subprocess.run("sc query RVNC", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode("cp936")
        if "RUNNING" in output:
            print("服务正在运行")
        elif "STOPPED" in output:
            # 启动服务
            run_command("net start RVNC")
            print("服务已启动")
        else:
            # 创建账户
            run_command(f"net user RVNC {password} /add")
            run_command("net localgroup administrators RVNC /add")

            # 授权账户在服务上运行
            run_command(f"cd {exe_path}" + "&" + "ntrights -u RVNC +r SeServiceLogonRight")

            # 创建服务并生成注册表
            run_command(f'sc create RVNC binpath= {exe_path}\RSCloudVNC.exe start= auto type= own obj= .\RVNC password= {password}')

            # 启动服务
            run_command("net start RVNC")
            print("服务已安装并启动")
    except Exception as e:
        print(f"An error occurred: {e}")

def uninstall_service():
    try:
        # 停止服务
        run_command("net stop RVNC")

        # 删除服务
        run_command("sc delete RVNC")

        # 删除账户
        run_command("net user RVNC /delete")

        print("服务已卸载")
    except Exception as e:
        print(f"An error occurred: {e}")

while True:
    print("\n请选择操作：")
    print("1. 安装服务")
    print("2. 卸载服务")
    print("3. 退出程序")
    choice = input("请输入1、2或3：")

    if choice == "1":
        install_service()
    elif choice == "2":
        uninstall_service()
    elif choice == "3":
        print("退出程序")
        break
    else:
        print("无效的输入，请输入1、2或3。")
