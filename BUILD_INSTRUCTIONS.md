# NormSpecGen - Build Instructions

These instructions are for developers who want to run NormSpecGen from source or build the standalone Windows executable.

## Requirements

- Windows
- Python 3.7 or newer

## Set Up the Development Environment

From the repository root:

```powershell
cd NormSpecGen
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks script activation for the current session, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

## Run from Source

With the virtual environment active:

```powershell
python main.py
```

## Check the Python Files

```powershell
python -m py_compile main.py map_generator.py
```

## Build the Windows Executable

Before each release, update `__version__` in `version.py`. This is the single
source of the version displayed in the application window title and is included
automatically in the executable. Rebuild the executable after changing it.
Use `MAJOR.MINOR.PATCH`: increment PATCH for fixes, MINOR for new features,
and MAJOR for incompatible changes. The initial version is `0.1.0`.

Run the automated tests before building (no additional test dependencies or GUI
window required):

```powershell
python -m unittest discover -s tests -v
```

The build script uses `.venv` when available and otherwise falls back to the `python` command. It requires PyInstaller.

Install PyInstaller into the active environment if needed:

```powershell
python -m pip install pyinstaller
```

Build the executable:

```powershell
.\build_exe.bat
```

The finished application is written to:

```text
dist\NormSpecGen.exe
```

The build uses `NormSpecGen.spec` and creates or refreshes the `build` and `dist` directories. The generated executable is a windowed application and does not open a console window.
