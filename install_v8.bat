@echo off
call conda activate e57-fusion-viewer
pip uninstall -y e57-fusion-viewer
pip install -e .
pause
