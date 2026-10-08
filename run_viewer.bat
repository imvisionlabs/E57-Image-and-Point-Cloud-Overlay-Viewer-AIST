@echo off
setlocal EnableExtensions
pushd "%~dp0" || exit /b 1
set "VIEWER_EXIT_CODE=0"

call conda activate e57-fusion-viewer
if errorlevel 1 goto activation_failed
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
python -m e57_fusion_viewer.main %*
set "VIEWER_EXIT_CODE=%errorlevel%"
goto finish

:activation_failed
echo ERROR: Could not activate e57-fusion-viewer. See docs\setup.md.
set "VIEWER_EXIT_CODE=1"

:finish
popd
if not defined E57_VIEWER_NO_PAUSE pause
exit /b %VIEWER_EXIT_CODE%
