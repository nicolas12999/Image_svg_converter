from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMessageBox,
    QStatusBar, QHBoxLayout, QWidget,
)

from app.core.app_settings import get_app_settings
from app.core.converter import convert
from app.core.settings import ConversionSettings
from app.i18n import tr
from app.ui.controls_panel import ControlsPanel
from app.ui.drop_zone import DropZone
from app.ui.preview_panel import PreviewPanel
from app.ui.styles import STYLESHEETS


class _ConversionThread(QThread):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, path: str, settings: ConversionSettings, parent=None) -> None:
        super().__init__(parent)
        self._path = path
        self._settings = settings

    def run(self) -> None:
        try:
            self.finished.emit(convert(Path(self._path), self._settings))
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PNG/JPG → SVG Converter")
        self.resize(1300, 820)
        self.setMinimumSize(960, 620)

        self._src_path: str | None = None
        self._svg_string: str | None = None
        self._thread: _ConversionThread | None = None

        cfg = get_app_settings()
        self.setStyleSheet(STYLESHEETS[cfg.theme])

        self._build_ui()

        cfg.language_changed.connect(self._retranslate)
        cfg.theme_changed.connect(self._apply_theme)
        self._retranslate()

    # ── build ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._drop = DropZone()
        self._drop.file_selected.connect(self._on_file_selected)
        root.addWidget(self._drop)

        self._controls = ControlsPanel()
        self._controls.convert_requested.connect(self._start_conversion)
        self._controls.export_requested.connect(self._export_svg)
        self._controls.settings_dialog_requested.connect(self._open_settings)
        root.addWidget(self._controls)

        self._preview = PreviewPanel()
        root.addWidget(self._preview, 1)

        self.setStatusBar(QStatusBar())

    # ── slots ────────────────────────────────────────────────────────────────────

    def _retranslate(self) -> None:
        self.statusBar().showMessage(tr('status_ready'))

    def _apply_theme(self, theme: str) -> None:
        self.setStyleSheet(STYLESHEETS[theme])

    def _open_settings(self) -> None:
        from app.ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec()

    def _on_file_selected(self, path: str) -> None:
        self._src_path = path
        self._svg_string = None
        self._preview.set_original(path)
        self._preview.clear_svg()
        self._controls.enable_convert(True)
        self._controls.enable_export(False)
        self.statusBar().showMessage(tr('status_loaded').format(name=Path(path).name))

    def _start_conversion(self) -> None:
        if not self._src_path:
            return
        if self._thread and self._thread.isRunning():
            return

        self._controls.enable_convert(False)
        self._controls.enable_export(False)
        self.statusBar().showMessage(tr('status_converting'))

        self._thread = _ConversionThread(
            self._src_path, self._controls.settings(), parent=self
        )
        self._thread.finished.connect(self._on_conversion_done)
        self._thread.failed.connect(self._on_conversion_failed)
        self._thread.start()

    def _on_conversion_done(self, svg: str) -> None:
        self._svg_string = svg
        self._preview.set_svg(svg)
        self._controls.enable_convert(True)
        self._controls.enable_export(True)
        size_kb = len(svg.encode()) / 1024
        name = Path(self._src_path).name if self._src_path else ''
        self.statusBar().showMessage(
            tr('status_done').format(size_kb=size_kb, name=name)
        )

    def _on_conversion_failed(self, msg: str) -> None:
        self._controls.enable_convert(True)
        self.statusBar().showMessage(tr('status_error').format(msg=msg))
        QMessageBox.critical(self, tr('dlg_error_title'), msg)

    def _export_svg(self) -> None:
        if not self._svg_string:
            return
        default = str(Path(self._src_path).with_suffix('.svg')) if self._src_path else ''
        path, _ = QFileDialog.getSaveFileName(
            self, tr('dlg_export_title'), default, tr('svg_filter')
        )
        if path:
            Path(path).write_text(self._svg_string, encoding='utf-8')
            self.statusBar().showMessage(
                tr('status_exported').format(name=Path(path).name)
            )
