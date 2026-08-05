@echo off
call conda activate e57-fusion-viewer
set PYTHONPATH=%CD%\src;%PYTHONPATH%
python tools\extract_images_from_e57_xml.py --e57 sample.e57 --out prepared_dataset
python tools\convert_points_with_pye57.py --e57 sample.e57 --out prepared_dataset\points.npz --scan-index 0 --max-points 500000
pause
