%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit

cd %~dp0bin

ntrights -u RVNC +r SeServiceLogonRight


pause