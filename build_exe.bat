@echo off
setlocal

pushd "%~dp0"

set "PYTHON_EXE="

if exist ".venv\Scripts\python.exe" (
  set "PYTHON_EXE=.venv\Scripts\python.exe"
)

if not defined PYTHON_EXE (
  set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  echo PyInstaller is not available in this Python environment.
  echo Run: %PYTHON_EXE% -m pip install pyinstaller
  popd
  exit /b 1
)

echo Building NormSpecGen.exe with PyInstaller...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean NormSpecGen.spec

if errorlevel 1 (
  echo Build failed.
  popd
  exit /b 1
)

echo.
echo Build complete.
echo EXE output: dist\NormSpecGen.exe

popd
