from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from app.core.app_settings import get_app_settings
from app.i18n import tr
from app.ui.styles import THEME_COLORS

SUPPORTED = {'.png', '.jpg', '.jpeg'}


def _drop_style(theme: str, hovered: bool = False) -> str:
    c = THEME_COLORS[theme]
    border = c['drop_border_hover'] if hovered else c['drop_border']
    bg = c['drop_bg_hover'] if hovered else c['drop_bg']
    return (
        f"DropZone {{ border: 2px dashed {border}; "
        f"border-radius: 12px; background-color: {bg}; }}"
    )


class DropZone(QWidget):
    file_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumWidth(200)
        self._build_ui()

        cfg = get_app_settings()
        cfg.language_changed.connect(self.retranslate_ui)
        cfg.theme_changed.connect(self._apply_theme)
        self._apply_theme(cfg.theme)
        self.retranslate_ui()

    # ── build ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 30, 20, 30)

        icon = QLabel("🖼")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 48px; background: transparent;")

        self._hint = QLabel()
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet("color: #6c7086; font-size: 12px; background: transparent;")

        self._filename = QLabel("")
        self._filename.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._filename.setWordWrap(True)
        self._filename.setStyleSheet(
            "color: #a6e3a1; font-size: 11px; background: transparent;"
        )

        self._browse_btn = QPushButton()
        self._browse_btn.setObjectName("secondary")
        self._browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._browse_btn.clicked.connect(self._browse)

        layout.addWidget(icon)
        layout.addWidget(self._hint)
        layout.addWidget(self._filename)
        layout.addWidget(self._browse_btn)

    # ── slots ────────────────────────────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self._hint.setText(tr('drop_hint'))
        self._browse_btn.setText(tr('browse_file'))

    def _apply_theme(self, theme: str | None = None) -> None:
        if theme is None:
            theme = get_app_settings().theme
        self.setStyleSheet(_drop_style(theme, hovered=False))

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr('open_image_title'),
            "",
            tr('images_filter'),
        )
        if path:
            self._accept(path)

    def _accept(self, path: str) -> None:
        self._filename.setText(Path(path).name)
        self.file_selected.emit(path)

    # ── drag & drop ──────────────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls()]
            if any(Path(p).suffix.lower() in SUPPORTED for p in paths):
                event.acceptProposedAction()
                self.setStyleSheet(
                    _drop_style(get_app_settings().theme, hovered=True)
                )
                return
        event.ignore()

    def dragLeaveEvent(self, _) -> None:
        self._apply_theme()

    def dropEvent(self, event: QDropEvent) -> None:
        self._apply_theme()
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if Path(path).suffix.lower() in SUPPORTED:
                self._accept(path)
                break
