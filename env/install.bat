@echo off
setlocal EnableExtensions

rem Resolve all project paths relative to this script.
pushd "%~dp0.." || exit /b 1
set "INSTALL_EXIT_CODE=0"

call conda activate e57-fusion-viewer
if errorlevel 1 goto install_failed
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto install_failed
python -m pip install -e .
if errorlevel 1 goto install_failed
echo Installation completed successfully.
goto finish

:install_failed
echo ERROR: Installation failed. See the error above and docs\setup.md.
set "INSTALL_EXIT_CODE=1"

:finish
popd
if not defined E57_SETUP_NO_PAUSE pause
exit /b %INSTALL_EXIT_CODE%
