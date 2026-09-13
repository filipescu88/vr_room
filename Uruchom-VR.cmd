@echo off
where pwsh.exe >nul 2>nul
if not errorlevel 1 (
  pwsh.exe -NoProfile -File "%~dp0scripts\Start-VR.ps1"
) else if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe" -NoProfile -File "%~dp0scripts\Start-VR.ps1"
) else (
  echo Zainstaluj PowerShell 7 oraz Node.js i uruchom ponownie.
)
pause
