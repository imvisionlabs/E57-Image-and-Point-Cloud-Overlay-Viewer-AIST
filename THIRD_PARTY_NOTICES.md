# Third-party software

Copyright 2026 National Institute of Advanced Industrial Science and Technology (AIST).

The original application code, scripts, configuration, and original documentation
are licensed under [Apache-2.0](LICENSE), unless stated otherwise. Logos,
trademarks, image assets, and data shown in screenshots are excluded from that
grant. Third-party components retain their own licenses and copyright notices.

## Bundled components

| Component | License / purpose |
| --- | --- |
| CPython | PSF license and included notices; Python runtime |
| Microsoft Visual C++ runtime | Microsoft license terms; Windows runtime |
| OpenSSL | Apache-2.0 and notices for the included 3.x runtime |
| NumPy | BSD-3-Clause and bundled native-library notices |
| Pillow | HPND (PIL license) and bundled codec notices |
| PySide6 / Shiboken6 / Qt Core, Gui, Widgets, Network, Svg | LGPLv3 option for eligible components, plus third-party notices |
| pye57 / libE57Format / CRCpp | MIT / BSD-3-Clause / MIT |
| Xerces-C++ | Apache-2.0; XML library in the Windows pye57 wheel |
| pyquaternion | MIT |
| PyInstaller | GPL-2.0-or-later with the bootloader distribution exception |

The Windows build copies notices from the actual Python distributions, including
support packages found by PyInstaller. `third_party_licenses/INDEX.md` in the
generated application records versions, license links, and native library paths.
Keep this document, `LICENSE`, and `third_party_licenses/` with the application.

## Qt / PySide6 source and replacement

Eligible Qt/PySide6 components are distributed under LGPLv3. Copies of LGPLv3
and GPLv3 (which LGPLv3 supplements) are in `third_party_licenses/`.
Users may replace these libraries with compatible modified versions and reverse
engineer the application to debug those modifications.

1. Back up the extracted application folder and close the viewer.
2. Read `third_party_licenses/INDEX.md` for the Python, Qt, PySide6, and Shiboken6
   versions and DLL/PYD paths. Build compatible Windows x64 replacements,
   preserving the Python and binding ABI, Qt compatibility, and compiler runtime.
3. Replace the corresponding DLLs, bindings, and plugins under `_internal/`,
   keeping their relative paths. Replace dependent bindings together if needed.
4. Run `E57-Image-and-Point-Cloud-Overlay-Viewer.exe --smoke-test`, then verify
   normal image display, E57 preprocessing, and dialogs. If necessary, rebuild
   the application from source with the replacement libraries using `env/build_exe.bat`.

Before publishing a binary release, provide the complete corresponding source
of its LGPL components, patches (if any), and necessary build/installation
information. Host the matching sources alongside the application ZIP and link
them in the Release. Upstream links alone do not complete this distribution step.
This document is not an offer to provide source at a future date.

The notices currently cover Qt/PySide6 6.11.1 and pye57 0.4.19. Their upstream
sources are listed below. Update the notices and source package when changing
these versions; verify source availability and library replacement before release.

| Source | Official archive |
| --- | --- |
| Qt Base | [6.11.1](https://download.qt.io/archive/qt/6.11/6.11.1/submodules/qtbase-everywhere-src-6.11.1.tar.xz) |
| Qt SVG | [6.11.1](https://download.qt.io/archive/qt/6.11/6.11.1/submodules/qtsvg-everywhere-src-6.11.1.tar.xz) |
| Qt Image Formats | [6.11.1](https://download.qt.io/archive/qt/6.11/6.11.1/submodules/qtimageformats-everywhere-src-6.11.1.tar.xz) |
| PySide6 / Shiboken6 | [6.11.1](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.11.1-src/pyside-setup-everywhere-src-6.11.1.tar.xz) |
| pye57 / libE57Format / CRCpp | [pye57 0.4.19 source distribution](https://pypi.org/project/pye57/0.4.19/#files) |
| Xerces-C++ | [3.2.3](https://archive.apache.org/dist/xerces/c/3/sources/xerces-c-3.2.3.tar.gz) |
| OpenSSL | [3.0.13 LICENSE and AUTHORS](https://github.com/openssl/openssl/tree/openssl-3.0.13) |

Qt notices preserve source license and attribution texts from the four Qt
archives above, including some components not present in every build. E57 native
notices preserve the pye57 source's libE57Format/CRCpp and Xerces-C++ notices.
Use the generated INDEX for the actual binary contents. Build instructions:
[Qt for Windows](https://doc.qt.io/qt-6/windows-building.html) and
[Qt for Python](https://doc.qt.io/qtforpython-6/building_from_source/index.html).

## Microsoft runtime

`third_party_licenses/Microsoft-VC-Runtime-NOTICES.txt` preserves the runtime
terms and their original document URLs. These apply only to Microsoft's
components; they do not restrict the LGPL replacement/debugging rights above.
Distributors must verify redistribution rights under their applicable Visual
Studio / Build Tools license and Microsoft's distributable code list. Runtime
end-user terms alone do not grant redistribution rights.
