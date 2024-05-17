@echo off
::删除账户
net user RVNC /del

::停止服务
sc stop RVNC

::删除服务
sc delete RVNC

::reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\RVNC"
pause