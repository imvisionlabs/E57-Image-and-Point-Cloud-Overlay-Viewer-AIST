@echo off
call conda activate e57-fusion-viewer
set PYTHONPATH=%CD%\src;%PYTHONPATH%
python -m e57_fusion_viewer.main
pause
