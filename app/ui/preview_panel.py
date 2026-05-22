from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSplitter, QVBoxLayout, QWidget,
)

from app.core.app_settings import get_app_settings
from app.i18n import tr
from app.ui.styles import THEME_COLORS


class _ImagePane(QScrollArea):
    """Scrollable, zoomable pane displaying a QPixmap."""

    def __init__(self, title_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title_key = title_key
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        self.setWidget(container)
        self.setWidgetResizable(True)

        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title_lbl = QLabel()
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._img = QLabel()
        self._img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img.setObjectName("placeholder")

        vbox.addWidget(self._title_lbl)
        vbox.addWidget(self._img, 1)

        self._source: QPixmap | None = None
        self._zoom = 1.0

        cfg = get_app_settings()
        cfg.language_changed.connect(self.retranslate_ui)
        cfg.theme_changed.connect(self._apply_theme)
        self._apply_theme(cfg.theme)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self._title_lbl.setText(tr(self._title_key))
        if self._source is None:
            self._img.setText(tr('no_image'))

    def _apply_theme(self, theme: str | None = None) -> None:
        if theme is None:
            theme = get_app_settings().theme
        c = THEME_COLORS[theme]
        self._title_lbl.setStyleSheet(
            f"color: {c['pane_title']}; font-size: 10px; font-weight: bold; "
            f"letter-spacing: 1px; padding: 4px; background: {c['pane_bg']};"
        )
        if self._source is None:
            self._img.setStyleSheet(
                f"background: {c['pane_bg']}; padding: 40px; "
                f"color: {c['pane_title']}; font-size: 13px;"
            )
        else:
            self._img.setStyleSheet(f"background: {c['pane_bg']}; padding: 12px;")

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self._source = pixmap
        theme = get_app_settings().theme
        c = THEME_COLORS[theme]
        self._img.setStyleSheet(f"background: {c['pane_bg']}; padding: 12px;")
        self._refresh()

    def set_zoom(self, zoom: float) -> None:
        self._zoom = max(0.05, min(8.0, zoom))
        self._refresh()

    def clear(self) -> None:
        self._source = None
        self._img.clear()
        self._apply_theme()
        self.retranslate_ui()

    def _refresh(self) -> None:
        if self._source is None:
            return
        target = self._source.size() * self._zoom
        scaled = self._source.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._img.setPixmap(scaled)


def _link_scroll(a: _ImagePane, b: _ImagePane) -> None:
    def sync_h(v: int) -> None:
        bar = b.horizontalScrollBar()
        bar.blockSignals(True)
        bar.setValue(v)
        bar.blockSignals(False)

    def sync_v(v: int) -> None:
        bar = b.verticalScrollBar()
        bar.blockSignals(True)
        bar.setValue(v)
        bar.blockSignals(False)

    a.horizontalScrollBar().valueChanged.connect(sync_h)
    a.verticalScrollBar().valueChanged.connect(sync_v)


class PreviewPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._zoom = 1.0
        self._svg_string: str | None = None
        self._build_ui()

        cfg = get_app_settings()
        cfg.language_changed.connect(self.retranslate_ui)
        self.retranslate_ui()

    # ── build ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QHBoxLayout()

        self._heading = QLabel()
        self._heading.setObjectName("heading")

        self._zoom_lbl = QLabel("100%")
        self._zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_lbl.setFixedWidth(50)
        self._zoom_lbl.setStyleSheet("color: #6c7086; font-size: 12px;")

        self._btn_minus = QPushButton("−")
        self._btn_minus.setObjectName("secondary")
        self._btn_minus.setFixedSize(28, 28)
        self._btn_minus.clicked.connect(lambda: self._zoom_by(0.8))

        self._btn_plus = QPushButton("+")
        self._btn_plus.setObjectName("secondary")
        self._btn_plus.setFixedSize(28, 28)
        self._btn_plus.clicked.connect(lambda: self._zoom_by(1.25))

        self._btn_fit = QPushButton("1:1")
        self._btn_fit.setObjectName("secondary")
        self._btn_fit.clicked.connect(self._zoom_reset)

        header.addWidget(self._heading)
        header.addStretch()
        header.addWidget(self._btn_minus)
        header.addWidget(self._zoom_lbl)
        header.addWidget(self._btn_plus)
        header.addWidget(self._btn_fit)
        layout.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)

        self._orig = _ImagePane('pane_original')
        self._svg = _ImagePane('pane_svg')

        splitter.addWidget(self._orig)
        splitter.addWidget(self._svg)
        splitter.setSizes([1, 1])

        _link_scroll(self._orig, self._svg)
        _link_scroll(self._svg, self._orig)

        layout.addWidget(splitter, 1)

    # ── retranslation ─────────────────────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self._heading.setText(tr('preview_heading'))
        self._btn_minus.setToolTip(tr('tt_zoom_out'))
        self._btn_plus.setToolTip(tr('tt_zoom_in'))
        self._btn_fit.setToolTip(tr('tt_zoom_reset'))

    # ── public API ───────────────────────────────────────────────────────────────

    def set_original(self, path: str) -> None:
        px = QPixmap(path)
        if px.isNull():
            return
        self._orig.set_pixmap(px)
        self._orig.set_zoom(self._zoom)

    def set_svg(self, svg_string: str) -> None:
        self._svg_string = svg_string
        self._render_svg()

    def clear_svg(self) -> None:
        self._svg_string = None
        self._svg.clear()

    # ── internals ────────────────────────────────────────────────────────────────

    def _render_svg(self) -> None:
        if not self._svg_string:
            return
        data = QByteArray(self._svg_string.encode('utf-8'))
        renderer = QSvgRenderer(data)
        if not renderer.isValid():
            self._svg.clear()
            return

        vb = renderer.viewBoxF()
        w = max(1, int(vb.width()) if vb.isValid() else 800)
        h = max(1, int(vb.height()) if vb.isValid() else 600)

        pixmap = QPixmap(w, h)
        pixmap.fill(QColor(255, 255, 255))
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, w, h))
        painter.end()

        self._svg.set_pixmap(pixmap)
        self._svg.set_zoom(self._zoom)

    def _zoom_by(self, factor: float) -> None:
        self._zoom = max(0.05, min(8.0, self._zoom * factor))
        self._apply_zoom()

    def _zoom_reset(self) -> None:
        self._zoom = 1.0
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        self._zoom_lbl.setText(f"{int(self._zoom * 100)}%")
        self._orig.set_zoom(self._zoom)
        self._svg.set_zoom(self._zoom)
