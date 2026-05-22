#!/usr/bin/env python3
"""GUI launcher — run this to open the graphical converter."""

import sys


def _check_deps() -> None:
    missing = []
    try:
        import PySide6  # noqa: F401
    except ImportError:
        missing.append("PySide6")
    try:
        import vtracer  # noqa: F401
    except ImportError:
        missing.append("vtracer")
    if missing:
        print(
            f"Dependencias faltantes: {', '.join(missing)}\n"
            "Instala con:  .venv/bin/pip install " + " ".join(missing),
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    _check_deps()

    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("SVG Converter")
    app.setOrganizationName("local")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
