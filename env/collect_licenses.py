# Copyright 2026 National Institute of Advanced Industrial Science and Technology (AIST).
# SPDX-License-Identifier: Apache-2.0
"""Copy notices for the actual Windows build; publication also requires sources."""
import argparse
import ast
from importlib import metadata
from pathlib import Path
import re
import shutil
import ssl
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {"PySide6": "6.11.1", "shiboken6": "6.11.1", "pye57": "0.4.19"}
QT_DLLS = {"qt6core.dll", "qt6gui.dll", "qt6widgets.dll", "qt6network.dll", "qt6svg.dll"}


def inputs():
    from PySide6.QtCore import qVersion

    for name, version in VERSIONS.items():
        if metadata.version(name).strip() != version:
            raise RuntimeError(f"{name} must match the supplied notices ({version}); update notices before changing versions")
    if qVersion() != VERSIONS["PySide6"]:
        raise RuntimeError("Qt version does not match its supplied notices")
    files = [(ROOT / name, Path(name)) for name in ("LICENSE", "THIRD_PARTY_NOTICES.md")]
    for name in ("LGPL-3.0-only.txt", "GPL-3.0-only.txt", "Qt-6.11.1-NOTICES.txt",
                 "E57-native-NOTICES.txt", "Microsoft-VC-Runtime-NOTICES.txt",
                 f"OpenSSL-{ssl.OPENSSL_VERSION.split()[1]}-NOTICES.txt"):
        relative = Path("third_party_licenses") / name
        files.append((ROOT / relative, relative))
    python_license = next((base / name for base in (Path(sys.base_prefix), Path(sys.prefix))
                           for name in ("LICENSE.txt", "LICENSE_PYTHON.txt", "LICENSE")
                           if (base / name).is_file()), None)
    if python_license is None:
        raise RuntimeError("Python runtime license not found in the build environment")
    files.append((python_license, Path("third_party_licenses/CPython/LICENSE.txt")))
    for source, _ in files:
        if not source.is_file() or not source.stat().st_size:
            raise RuntimeError(f"Missing license document: {source}")
    return files


def included_distributions():
    """Identify support packages as well as the explicitly used dependencies."""
    analysis = ast.literal_eval((ROOT / "build/viewer/Analysis-00.toc").read_text(encoding="utf-8"))
    sources = set()

    def visit(value):
        if isinstance(value, (tuple, list)):
            if len(value) == 3 and all(isinstance(x, str) for x in value) and value[2] in {
                "PYMODULE", "PYSOURCE", "EXTENSION", "BINARY", "DATA"
            }:
                sources.add(str(Path(value[1]).resolve()).lower())
            else:
                for item in value:
                    visit(item)

    visit(analysis)
    names = {"numpy", "pillow", "pyside6", "shiboken6", "pye57", "pyquaternion",
             "pyinstaller", "pyinstaller-hooks-contrib"}
    for dist in metadata.distributions():
        if any(str(Path(dist.locate_file(f)).resolve()).lower() in sources for f in dist.files or ()):
            names.add(re.sub(r"[-_.]+", "-", dist.metadata["Name"]).lower())
    return [metadata.distribution(name) for name in sorted(names)]


def collect(output):
    files = inputs()
    internal = output / "_internal"
    if not internal.is_dir() or not (output / "E57-Image-and-Point-Cloud-Overlay-Viewer.exe").is_file():
        raise RuntimeError("Expected a complete standalone application folder")
    if (output / "third_party_licenses").exists():
        raise RuntimeError("License output already exists; rebuild into a clean application folder")
    binaries = sorted(p for p in internal.rglob("*") if p.suffix.lower() in (".dll", ".pyd"))
    unexpected = [p.name for p in binaries if p.name.lower().startswith("qt6") and p.name.lower() not in QT_DLLS]
    if unexpected:
        raise RuntimeError("Additional Qt modules need license review: " + ", ".join(unexpected))
    rows = ["# Bundled software", "", f"Python: {sys.version.split()[0]}; {ssl.OPENSSL_VERSION}", "",
            "| Distribution | Version |", "| --- | --- |"]
    for dist in included_distributions():
        notices = []
        for entry in dist.files or ():
            relative = Path(str(entry))
            if relative.is_absolute() or ".." in relative.parts:
                continue
            if any(re.match(r"(?i)^(licen[cs]e|copying|copyright|notice|authors)([._-]|$)", part)
                   or part.lower() == "licenses" for part in relative.parts):
                source = Path(dist.locate_file(entry))
                if source.is_file():
                    notices.append((source, Path("third_party_licenses") / dist.metadata["Name"] / relative))
        if not notices:
            raise RuntimeError(f"No license documents found for {dist.metadata['Name']}")
        files.extend(notices)
        rows.append(f"| {dist.metadata['Name']} | {dist.version} |")
    for source, relative in files:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    rows += ["", "## License documents", "", "- [Application license](../LICENSE)",
             "- [Third-party notices and library replacement](../THIRD_PARTY_NOTICES.md)"]
    rows += [f"- [{relative.as_posix()}]({relative.relative_to('third_party_licenses').as_posix()})"
             for _, relative in files if relative.parts[0] == "third_party_licenses"]
    rows += ["", "## DLL / PYD paths (relative to the application folder)", ""]
    rows += [f"- `{p.relative_to(output).as_posix()}`" for p in binaries]
    (output / "third_party_licenses/INDEX.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--check", action="store_true", help="Check environment versions and supplied notices before building")
    args = parser.parse_args()
    if not args.check and args.output is None:
        parser.error("provide an application folder or --check")
    try:
        inputs() if args.check else collect(args.output.resolve())
    except (RuntimeError, OSError, metadata.PackageNotFoundError) as exc:
        parser.exit(1, f"License collection failed: {exc}\n")
    print("License documents checked." if args.check else "License documents copied; complete source distribution before publication.")
