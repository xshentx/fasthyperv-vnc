@echo off


set /p password=请输入密码：

::创建账户
net user RVNC %password% /add

net /add localgroup administrators RVNC

::授权账户在服务上运行
cd %~dp0bin
ntrights -u RVNC +r SeServiceLogonRight

::创建服务并生成注册表
sc create RVNC binpath= "%~dp0bin\RSCloudVNC.exe" start= auto type= own obj= .\RVNC password= %password%

net start RVNC

pause