import sys

from e57_fusion_viewer.main import main


def smoke_test() -> None:
    """Import packaged native dependencies without opening the GUI."""
    import pye57  # noqa: F401
    from PySide6.QtCore import qVersion

    if not qVersion():
        raise RuntimeError("Qt runtime version is unavailable")


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        smoke_test()
        raise SystemExit(0)
    raise SystemExit(main())
