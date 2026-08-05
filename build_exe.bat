@echo off
setlocal
call conda activate e57-fusion-viewer
if errorlevel 1 (
  echo Failed to activate conda environment: e57-fusion-viewer
  pause
  exit /b 1
)

python -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo Failed to install or upgrade PyInstaller.
  pause
  exit /b 1
)

python -m PyInstaller E57FusionViewer.spec --clean --noconfirm
if errorlevel 1 (
  echo PyInstaller build failed.
  pause
  exit /b 1
)

echo.
echo Build completed.
echo Output folder:
echo   dist\E57FusionViewer\
echo.
echo Distribute the whole dist\E57FusionViewer folder as a ZIP.
echo Users can launch:
echo   E57FusionViewer.exe
pause
