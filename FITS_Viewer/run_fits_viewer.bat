@echo off
setlocal
set "PYTHON_EXE=F:\Documentos\Python\.venv\Scripts\python.exe"
set "SCRIPT_DIR=%~dp0"
if "%~1"=="" (
  "%PYTHON_EXE%" "%SCRIPT_DIR%fits_viewer.py"
) else (
  set "FITS_FOLDER=%~1"
  "%PYTHON_EXE%" "%SCRIPT_DIR%fits_viewer.py" --folder "%FITS_FOLDER%"
)
set "EXITCODE=%ERRORLEVEL%"
pause
exit /b %EXITCODE%
