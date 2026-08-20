@echo off
setlocal EnableExtensions

rem Always build from the repository root, even when this file is double-clicked.
pushd "%~dp0"

set "BUILD_VENV=%~dp0.build-venv"
set "LOCAL_BUILD_PYTHON=%BUILD_VENV%\Scripts\python.exe"
set "BUILD_PYTHON="
set "BOOTSTRAP_PYTHON="
set "BUILD_EXIT_CODE=0"
set "APP_NAME=E57-Image-and-Point-Cloud-Overlay-Viewer"
set "SPEC_FILE=%APP_NAME%.spec"

echo ========================================
echo %APP_NAME% standalone build
echo ========================================
echo.

rem Reuse a healthy local build environment.
if exist "%LOCAL_BUILD_PYTHON%" (
  call :check_ready_python "%LOCAL_BUILD_PYTHON%"
  if not errorlevel 1 (
    set "BUILD_PYTHON=%LOCAL_BUILD_PYTHON%"
    echo [1/4] Reusing the local build environment...
    goto build_application
  )
  echo [1/4] The existing local build environment is not usable.
)

rem Prefer a caller-supplied interpreter.
if defined E57_BUILD_PYTHON (
  call :check_ready_python "%E57_BUILD_PYTHON%"
  if not errorlevel 1 (
    set "BUILD_PYTHON=%E57_BUILD_PYTHON%"
    echo [1/4] Using E57_BUILD_PYTHON...
    goto prepare_existing_environment
  )
  call :check_native_python "%E57_BUILD_PYTHON%"
  if not errorlevel 1 set "BOOTSTRAP_PYTHON=%E57_BUILD_PYTHON%"
)

rem Prefer the Windows Python Launcher when Python 3.11 is installed.
if not defined BOOTSTRAP_PYTHON (
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3.11 -c "import pathlib, struct, sys; raise SystemExit(0 if struct.calcsize('P') == 8 and not (pathlib.Path(sys.prefix) / 'conda-meta').is_dir() else 1)" >nul 2>&1
    if not errorlevel 1 goto create_with_python_launcher
  )
)

rem Check Python available on PATH and common python.org locations.
if not defined BOOTSTRAP_PYTHON (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import pathlib, struct, sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8 and not (pathlib.Path(sys.prefix) / 'conda-meta').is_dir() else 1)" >nul 2>&1
    if not errorlevel 1 set "BOOTSTRAP_PYTHON=python"
  )
)
if not defined BOOTSTRAP_PYTHON call :select_native_python "%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined BOOTSTRAP_PYTHON call :select_native_python "%ProgramFiles%\Python311\python.exe"

if defined BOOTSTRAP_PYTHON goto create_with_python_path

rem A ready existing environment may be used directly without conda activation.
call :select_ready_python "%USERPROFILE%\anaconda3\envs\e57-fusion-viewer\python.exe"
if not defined BUILD_PYTHON call :select_ready_python "%USERPROFILE%\miniconda3\envs\e57-fusion-viewer\python.exe"
if not defined BUILD_PYTHON call :select_ready_python "%LocalAppData%\anaconda3\envs\e57-fusion-viewer\python.exe"
if not defined BUILD_PYTHON call :select_ready_python "%LocalAppData%\miniconda3\envs\e57-fusion-viewer\python.exe"
if not defined BUILD_PYTHON goto python_not_found

echo [1/4] Using an existing compatible Python environment...
goto prepare_existing_environment

:create_with_python_launcher
echo [1/4] Creating the local build environment with Python 3.11...
if exist "%BUILD_VENV%" rmdir /s /q "%BUILD_VENV%"
py -3.11 -m venv "%BUILD_VENV%"
if errorlevel 1 goto venv_failed
set "BUILD_PYTHON=%LOCAL_BUILD_PYTHON%"
goto install_dependencies

:create_with_python_path
echo [1/4] Creating the local build environment with Python 3.11...
if exist "%BUILD_VENV%" rmdir /s /q "%BUILD_VENV%"
"%BOOTSTRAP_PYTHON%" -m venv "%BUILD_VENV%"
if errorlevel 1 goto venv_failed
set "BUILD_PYTHON=%LOCAL_BUILD_PYTHON%"

:install_dependencies
echo [2/4] Installing build dependencies...
"%BUILD_PYTHON%" -m pip install --disable-pip-version-check --upgrade pip setuptools wheel
if errorlevel 1 goto dependency_failed
"%BUILD_PYTHON%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto dependency_failed
call :check_ready_python "%BUILD_PYTHON%"
if errorlevel 1 goto dependency_failed
goto build_application

:prepare_existing_environment
for %%I in ("%BUILD_PYTHON%") do set "BUILD_PREFIX=%%~dpI"
set "BUILD_PREFIX=%BUILD_PREFIX:~0,-1%"
if exist "%BUILD_PREFIX%\Library\bin" (
  set "PATH=%BUILD_PREFIX%;%BUILD_PREFIX%\Library\bin;%BUILD_PREFIX%\Scripts;%PATH%"
)
echo [2/4] Required build dependencies are available.

:build_application
echo [3/4] Building the standalone application...
"%BUILD_PYTHON%" -m PyInstaller "%SPEC_FILE%" --clean --noconfirm
if errorlevel 1 goto build_failed

echo [4/4] Verifying packaged files...
if not exist "dist\%APP_NAME%\%APP_NAME%.exe" goto output_missing
if not exist "dist\%APP_NAME%\_internal\PySide6\plugins\platforms\qwindows.dll" goto qt_plugin_missing
if not exist "dist\%APP_NAME%\_internal\tools\extract_images_from_e57_xml.py" goto tool_files_missing
if not exist "dist\%APP_NAME%\_internal\tools\convert_points_with_pye57.py" goto tool_files_missing
if not exist "dist\%APP_NAME%\_internal\assets\imvisionlabs-main-logoonly.png" goto icon_missing
dir /b "dist\%APP_NAME%\_internal\pye57\libe57*.pyd" >nul 2>&1
if errorlevel 1 goto pye57_missing

rem Newly generated unsigned executables may be blocked by corporate Device
rem Guard policies. Run the executable test only when explicitly requested.
if defined E57_RUN_EXE_SMOKE_TEST (
  echo Running the optional packaged dependency check...
  "dist\%APP_NAME%\%APP_NAME%.exe" --smoke-test
  if errorlevel 1 goto smoke_test_failed
) else (
  echo Packaged execution test skipped.
  echo To enable it on an unrestricted PC, set E57_RUN_EXE_SMOKE_TEST=1.
)

echo.
echo Build completed successfully.
echo Output folder:
echo   %~dp0dist\%APP_NAME%\
echo.
echo Distribute the entire %APP_NAME% folder.
echo The destination PC does not need Python, Conda, or pip.
echo Launch the Viewer with:
echo   %APP_NAME%.exe
goto finish

:select_native_python
call :check_native_python "%~1"
if not errorlevel 1 set "BOOTSTRAP_PYTHON=%~1"
exit /b 0

:select_ready_python
if not exist "%~1" exit /b 0
call :check_ready_python "%~1"
if not errorlevel 1 set "BUILD_PYTHON=%~1"
exit /b 0

:check_native_python
if not exist "%~1" exit /b 1
"%~1" -c "import pathlib, struct, sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8 and not (pathlib.Path(sys.prefix) / 'conda-meta').is_dir() else 1)" >nul 2>&1
exit /b %errorlevel%

:check_ready_python
if not exist "%~1" exit /b 1
"%~1" -c "import PIL, PyInstaller, PySide6.QtCore, numpy, pye57" >nul 2>&1
exit /b %errorlevel%

:python_not_found
echo.
echo ERROR: A usable 64-bit Python 3.11 installation was not found.
echo Install Python 3.11 from https://www.python.org/downloads/windows/
echo During installation, enable the Python Launcher or Add Python to PATH.
set "BUILD_EXIT_CODE=1"
goto finish

:venv_failed
echo.
echo ERROR: Failed to create the local build environment:
echo   %BUILD_VENV%
set "BUILD_EXIT_CODE=1"
goto finish

:dependency_failed
echo.
echo ERROR: Failed to install or import the build dependencies.
echo Check the network connection and pip error shown above.
set "BUILD_EXIT_CODE=1"
goto finish

:build_failed
echo.
echo ERROR: PyInstaller build failed.
set "BUILD_EXIT_CODE=1"
goto finish

:output_missing
echo.
echo ERROR: PyInstaller finished, but %APP_NAME%.exe was not found.
set "BUILD_EXIT_CODE=1"
goto finish

:qt_plugin_missing
echo.
echo ERROR: The Qt Windows platform plugin was not packaged.
echo The output is not standalone and will not be distributed.
set "BUILD_EXIT_CODE=1"
goto finish

:tool_files_missing
echo.
echo ERROR: The E57 preparation tool files were not packaged.
set "BUILD_EXIT_CODE=1"
goto finish

:pye57_missing
echo.
echo ERROR: The native pye57 module was not packaged.
set "BUILD_EXIT_CODE=1"
goto finish

:icon_missing
echo.
echo ERROR: The imvisionlabs application icon was not packaged.
set "BUILD_EXIT_CODE=1"
goto finish

:smoke_test_failed
echo.
echo ERROR: The packaged application failed its dependency check.
echo If Device Guard blocked the unsigned executable, rerun without
echo E57_RUN_EXE_SMOKE_TEST and ask your administrator about code signing
echo or an approved allow policy before distributing the application.
set "BUILD_EXIT_CODE=1"

:finish
echo.
popd
if not defined E57_BUILD_NO_PAUSE pause
exit /b %BUILD_EXIT_CODE%
