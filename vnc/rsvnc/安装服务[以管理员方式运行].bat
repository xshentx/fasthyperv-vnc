@echo off


set /p password=���������룺

::�����˻�
net user RVNC %password% /add

net /add localgroup administrators RVNC

::��Ȩ�˻��ڷ���������
cd %~dp0bin
ntrights -u RVNC +r SeServiceLogonRight

::������������ע���
sc create RVNC binpath= "%~dp0bin\RSCloudVNC.exe" start= auto type= own obj= .\RVNC password= %password%

net start RVNC

pause