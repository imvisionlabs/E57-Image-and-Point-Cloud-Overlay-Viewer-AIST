# E57-Image-and-Point-Cloud-Overlay-Viewer

**English** | [日本語](README_JP.md)

![E57 image with a point cloud overlay](docs/images/viewer-overlay-screenshot.png)

A Windows viewer that reads point clouds, images, and camera information from E57 files and overlays the points on images for inspection.

## Project layout

```text
.
├── README.md                  English usage guide and project overview
├── README_JP.md               Japanese usage guide and project overview
├── run_viewer.bat             Launch the viewer from source
├── pyproject.toml             Python package definition
├── src/e57_fusion_viewer/     Viewer and projection code
├── tools/                     E57 image extraction and point cloud conversion
├── env/                       Environment setup and distribution build
│   ├── install.bat
│   ├── build_exe.bat
│   ├── requirements.txt
│   ├── environment-win64-explicit.txt
│   ├── environment.yml
│   ├── viewer.spec
│   └── run_viewer_packaged.py
├── assets/                    Application image assets
└── docs/                      Guides (in Japanese) and README images
```

The `env` directory contains environment definitions and setup files. Conda creates the environment itself in its own managed location.

## Main features

- Select an E57 file in the viewer to prepare its images, camera information, and point clouds, then display them.
- Automatically select and overlay the point cloud from the scan associated with an image.
- Adjust point and image opacity, point size, and the number of displayed points.
- Click an image to display the XYZ coordinates of the nearest projected point.
- Reopen a prepared dataset to skip preprocessing.

## Run the Windows executable

Supported systems are 64-bit Windows 10 and 11. Python and Conda are not required.

1. Open [Releases](https://github.com/imvisionlabs/E57-Image-and-Point-Cloud-Overlay-Viewer-AIST/releases) and download the Windows ZIP from the release's `Assets`. For v0.8.0, the file is `e57-overlay-viewer-0.8.0-windows-x64.zip`.
2. Right-click the downloaded ZIP and select `Extract All`.
3. Open the `E57-Image-and-Point-Cloud-Overlay-Viewer` folder in the extracted files.
4. Double-click `E57-Image-and-Point-Cloud-Overlay-Viewer.exe`.

   If file extensions are hidden, `.exe` will not appear at the end of the name. Select the file whose type is "Application."

   ![Executable and _internal folder in the distribution folder](docs/images/viewer-executable.png)

5. Click `Open E57 and prepare` at the upper right of the viewer, then select the E57 file you want to display.

   ![Location of the Open E57 and prepare button](docs/images/viewer-open-e57.png)

Keep the EXE and the `_internal` folder together. The EXE will not start if you move it out of that folder. `Source code (zip)` under `Assets` contains the source code, not the Windows executable.

If your organization's Device Guard policy blocks the application, ask your IT support team to approve its use.

## Run from source

Use 64-bit Windows 10 or 11 with Anaconda or Miniconda. An internet connection is required for the initial setup.

After cloning or extracting the source, open **Anaconda Prompt**, change to the folder containing this README, and run:

```bat
conda create -n e57-fusion-viewer --file env\environment-win64-explicit.txt
env\install.bat
run_viewer.bat
```

`env\install.bat` activates the Conda environment you created and installs the dependencies and viewer. For later launches, run `run_viewer.bat`.

For manual setup, environment updates, and startup errors, see the [setup guide (Japanese)](docs/setup.md).

## Display an E57 file

1. In the right panel, use `prepare max points` to set the maximum number of points saved during preprocessing. The default is 500,000.
2. Click `Open E57 and prepare` and select the target `.e57` file.
3. When preprocessing finishes, the first image and point cloud appear. Large E57 files may take some time to process.
4. Use the `Image` dropdown to switch images.

The original E57 file is not modified. The prepared dataset is saved next to the E57 file with the following layout. The destination must have write permission and enough free space.

```text
<E57 filename>_prepared_dataset/
├── cameras.json
├── e57.xml
├── images/
├── points.npz
├── points_scan_000.npz
└── points_scan_001.npz   (if there are multiple scans)
```

To display the same E57 file again without repeating preprocessing, choose this folder with `Open prepared dataset`.

### Display controls

| Control | Description |
| --- | --- |
| `point alpha` | Changes the opacity of the point cloud. |
| `image alpha` | Changes the opacity of the background image. |
| `point size` | Changes the size of the drawn points. |
| `max overlay points` | Limits the number of points drawn over the image. A higher value produces a denser overlay but makes drawing slower. |
| `prepare max points` | Limits the number of points saved for each scan and for the combined cloud during preprocessing. A higher value can show more detail but increases processing time and memory use. |

Clicking the image displays the XYZ coordinates of the nearest projected point within 15 px of the click in the right panel.

### Preprocessing overview

1. Extract XML, images, and camera information from the E57 file.
2. Read point data in chunks of up to 200,000 points, select points, remove invalid points, and transform coordinates into the world frame.
3. Save per-scan and combined point clouds.
4. Select the point cloud for each image and project its points using the camera information.

For an image with no associated scan, the viewer uses the combined `points.npz` cloud. See the [E57 preprocessing guide (Japanese)](docs/e57-preprocessing-guide.md) for processing and coordinate transformation details.

### Display and preprocessing problems

**If preprocessing fails**, check whether another application is using the E57 file and whether the output location has write permission and enough free space. If memory is insufficient, lower `prepare max points` and try again. If an incomplete output folder remains, move it aside before retrying if needed.

**If points do not appear or do not align with the image**, check the projected point count and the active `points*.npz` file in the right panel. E57 exporters differ in how they record camera poses, coordinate axes, and scan associations, so some files may not overlay correctly.

The viewer uses the following projection convention, verified with Pentax E57 samples:

- Camera pose: camera-to-world
- Camera forward direction: `-Z`; up direction in camera coordinates: `+Y`
- Down direction in image coordinates: `+V`
- Principal point: use `principalPointX` and `principalPointY` recorded in the E57 file

Supported images are JPEG or PNG images with pose and pinhole camera information. The viewer does not provide manual correction of the projection convention or principal point. E57 files that use other conventions may require checking the exporter's specifications or converting the data.

## Distribution build and technical guides

To build the distributable Windows executable, run the following command from the repository root:

```bat
env\build_exe.bat
```

The output is `dist\E57-Image-and-Point-Cloud-Overlay-Viewer`. Distribute the entire folder.

- [Setup guide (Japanese)](docs/setup.md): initial setup, updates, dependency files, and startup errors
- [Distribution build guide (Japanese)](docs/build.md): build environment, output, and verification
- [E57 preprocessing guide (Japanese)](docs/e57-preprocessing-guide.md): image extraction, point cloud conversion, and camera projection
