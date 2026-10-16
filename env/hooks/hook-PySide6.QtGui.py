# Copyright 2026 National Institute of Advanced Industrial Science and Technology (AIST)
# SPDX-License-Identifier: Apache-2.0
"""Keep unused PDF and virtual keyboard plugins out of the viewer build."""
from pathlib import Path

from PyInstaller.utils.hooks.qt import add_qt6_dependencies

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)
# Qt Virtual Keyboard is not available under LGPL. Neither plugin is used by
# the viewer; exclude them before native dependency analysis collects their DLLs.
excluded = {"qpdf.dll", "qtvirtualkeyboardplugin.dll"}
binaries = [(source, target) for source, target in binaries
            if Path(source).name.lower() not in excluded]
