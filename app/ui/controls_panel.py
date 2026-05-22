from pathlib import Path

from PySide6.QtCore import Qt, QByteArray, Signal
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QVBoxLayout, QWidget,
)

from app.core.app_settings import get_app_settings
from app.core.presets import PRESETS
from app.core.settings import ConversionSettings
from app.i18n import tr
from app.ui.styles import THEME_COLORS

_GEAR_SVG = (
    Path(__file__).parent.parent.parent / "assets" / "icons" / "gear.svg"
).read_text()


def _make_icon(svg_source: str, color: str, size: int) -> QIcon:
    """Render an SVG string with 'currentColor' replaced by *color* into a QIcon."""
    colored = svg_source.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(colored.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

# Stable internal keys for the preset combo (order matters).
_PRESET_KEYS = ['Foto', 'Logo', 'Ilustración', 'Alta calidad', 'Borrador', 'B&N']
_PRESET_TR = {
    'Foto': 'preset_foto',
    'Logo': 'preset_logo',
    'Ilustración': 'preset_ilustracion',
    'Alta calidad': 'preset_alta_calidad',
    'Borrador': 'preset_borrador',
    'B&N': 'preset_byn',
}
_CUSTOM_KEY = '__custom__'


class _Slider(QWidget):
    """Horizontal slider with a fixed label and a live value readout."""

    valueChanged = Signal(float)

    def __init__(
        self,
        min_v: float,
        max_v: float,
        default: float,
        decimals: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._decimals = decimals
        self._scale = 10 ** decimals

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._lbl = QLabel()
        self._lbl.setFixedWidth(128)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(int(min_v * self._scale), int(max_v * self._scale))
        self._slider.setValue(int(default * self._scale))
        self._slider.setCursor(Qt.CursorShape.PointingHandCursor)

        self._val = QLabel(self._fmt(default))
        self._val.setObjectName("value")
        self._val.setFixedWidth(40)
        self._val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._slider.valueChanged.connect(self._on_change)

        row.addWidget(self._lbl)
        row.addWidget(self._slider, 1)
        row.addWidget(self._val)

    def _fmt(self, v: float) -> str:
        return f"{v:.{self._decimals}f}"

    def _on_change(self, raw: int) -> None:
        v = raw / self._scale
        self._val.setText(self._fmt(v))
        self.valueChanged.emit(v)

    def value(self) -> float:
        return self._slider.value() / self._scale

    def set_value(self, v: float, silent: bool = True) -> None:
        if silent:
            self._slider.blockSignals(True)
        self._slider.setValue(int(v * self._scale))
        self._val.setText(self._fmt(v))
        if silent:
            self._slider.blockSignals(False)

    def retranslate(self, label_key: str, tooltip_key: str) -> None:
        self._lbl.setText(tr(label_key))
        tip = tr(tooltip_key)
        self._lbl.setToolTip(tip)
        self._slider.setToolTip(tip)


class _Divider(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("divider")
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)


class ControlsPanel(QWidget):
    settings_changed = Signal(ConversionSettings)
    convert_requested = Signal()
    export_requested = Signal()
    settings_dialog_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(330)
        self._settings = ConversionSettings()
        self._preset_key = _PRESET_KEYS[0]  # tracks selected preset internal key
        self._build_ui()

        cfg = get_app_settings()
        cfg.language_changed.connect(self.retranslate_ui)
        cfg.theme_changed.connect(self._apply_gear_icon)
        self._apply_gear_icon(cfg.theme)
        self.retranslate_ui()

    # ── build ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(6)
        layout.setContentsMargins(16, 16, 16, 12)

        # title row with settings gear
        title_row = QHBoxLayout()
        self._heading = QLabel()
        self._heading.setObjectName("heading")
        self._settings_btn = QPushButton()
        self._settings_btn.setObjectName("secondary")
        self._settings_btn.setFixedSize(28, 28)
        self._settings_btn.setIconSize(self._settings_btn.size() * 0.6)
        self._settings_btn.clicked.connect(self.settings_dialog_requested)
        title_row.addWidget(self._heading)
        title_row.addStretch()
        title_row.addWidget(self._settings_btn)
        layout.addLayout(title_row)
        layout.addSpacing(4)

        # preset
        self._section_preset = QLabel()
        self._section_preset.setObjectName("section")
        layout.addWidget(self._section_preset)

        self._preset = QComboBox()
        self._preset.currentIndexChanged.connect(self._on_preset)
        layout.addWidget(self._preset)

        layout.addSpacing(4)
        layout.addWidget(_Divider())
        layout.addSpacing(4)

        # vectorization
        self._section_vec = QLabel()
        self._section_vec.setObjectName("section")
        layout.addWidget(self._section_vec)

        row_mode = QHBoxLayout()
        self._lbl_colormode = QLabel()
        row_mode.addWidget(self._lbl_colormode)
        self._colormode = QComboBox()
        row_mode.addWidget(self._colormode, 1)
        layout.addLayout(row_mode)

        row_hier = QHBoxLayout()
        self._lbl_hierarchical = QLabel()
        row_hier.addWidget(self._lbl_hierarchical)
        self._hierarchical = QComboBox()
        row_hier.addWidget(self._hierarchical, 1)
        layout.addLayout(row_hier)

        row_curve = QHBoxLayout()
        self._lbl_curves = QLabel()
        row_curve.addWidget(self._lbl_curves)
        self._mode_combo = QComboBox()
        row_curve.addWidget(self._mode_combo, 1)
        layout.addLayout(row_curve)

        layout.addSpacing(4)

        self._sl_color_precision = _Slider(1, 8, 6)
        self._sl_layer_difference = _Slider(0, 256, 16)
        self._sl_filter_speckle = _Slider(1, 32, 4)
        self._sl_corner_threshold = _Slider(0, 180, 60)
        self._sl_length_threshold = _Slider(0, 10, 4, decimals=1)

        for w in (
            self._sl_color_precision, self._sl_layer_difference,
            self._sl_filter_speckle, self._sl_corner_threshold,
            self._sl_length_threshold,
        ):
            layout.addWidget(w)

        layout.addSpacing(4)
        layout.addWidget(_Divider())
        layout.addSpacing(4)

        # enhancement
        self._section_enh = QLabel()
        self._section_enh.setObjectName("section")
        layout.addWidget(self._section_enh)

        self._sl_contrast = _Slider(0.5, 2.0, 1.0, decimals=2)
        self._sl_saturation = _Slider(0.0, 2.0, 1.0, decimals=2)
        self._sl_sharpness = _Slider(0.5, 2.0, 1.0, decimals=2)

        for w in (self._sl_contrast, self._sl_saturation, self._sl_sharpness):
            layout.addWidget(w)

        layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll, 1)

        # buttons (always visible, outside scroll)
        btn_area = QWidget()
        btn_layout = QVBoxLayout(btn_area)
        btn_layout.setContentsMargins(16, 8, 16, 16)
        btn_layout.setSpacing(8)

        self._convert_btn = QPushButton()
        self._convert_btn.setEnabled(False)

        self._export_btn = QPushButton()
        self._export_btn.setObjectName("secondary")
        self._export_btn.setEnabled(False)

        btn_layout.addWidget(self._convert_btn)
        btn_layout.addWidget(self._export_btn)
        outer.addWidget(btn_area)

        # wire signals
        self._convert_btn.clicked.connect(self.convert_requested)
        self._export_btn.clicked.connect(self.export_requested)

        for combo in (self._colormode, self._hierarchical, self._mode_combo):
            combo.currentIndexChanged.connect(self._on_manual_change)
        for slider in (
            self._sl_color_precision, self._sl_layer_difference,
            self._sl_filter_speckle, self._sl_corner_threshold,
            self._sl_length_threshold, self._sl_contrast,
            self._sl_saturation, self._sl_sharpness,
        ):
            slider.valueChanged.connect(self._on_manual_change)

    # ── icon ─────────────────────────────────────────────────────────────────────

    def _apply_gear_icon(self, theme: str | None = None) -> None:
        if theme is None:
            theme = get_app_settings().theme
        color = THEME_COLORS[theme]['icon']
        icon_px = 16  # rendered pixel size (button is 28×28, icon 16×16 = nice padding)
        self._settings_btn.setIcon(_make_icon(_GEAR_SVG, color, icon_px))

    # ── retranslation ─────────────────────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self._heading.setText(tr('panel_heading'))
        self._settings_btn.setToolTip(tr('tt_settings'))
        self._section_preset.setText(tr('section_preset'))
        self._section_vec.setText(tr('section_vectorize'))
        self._section_enh.setText(tr('section_enhance'))

        self._lbl_colormode.setText(tr('lbl_colormode'))
        self._lbl_hierarchical.setText(tr('lbl_hierarchical'))
        self._lbl_curves.setText(tr('lbl_curves'))

        self._retranslate_preset_combo()
        self._retranslate_combo(
            self._colormode,
            [tr('colormode_color'), tr('colormode_binary')],
            tr('tt_colormode'),
        )
        self._retranslate_combo(
            self._hierarchical,
            [tr('hier_stacked'), tr('hier_cutout')],
            tr('tt_hierarchical'),
        )
        self._retranslate_combo(
            self._mode_combo,
            [tr('mode_spline'), tr('mode_polygon'), tr('mode_none')],
            tr('tt_mode'),
        )

        self._sl_color_precision.retranslate('sl_color_precision', 'tt_color_precision')
        self._sl_layer_difference.retranslate('sl_layer_difference', 'tt_layer_difference')
        self._sl_filter_speckle.retranslate('sl_filter_speckle', 'tt_filter_speckle')
        self._sl_corner_threshold.retranslate('sl_corner_threshold', 'tt_corner_threshold')
        self._sl_length_threshold.retranslate('sl_length_threshold', 'tt_length_threshold')
        self._sl_contrast.retranslate('sl_contrast', 'tt_contrast')
        self._sl_saturation.retranslate('sl_saturation', 'tt_saturation')
        self._sl_sharpness.retranslate('sl_sharpness', 'tt_sharpness')

        is_converting = not self._convert_btn.isEnabled() and self._convert_btn.text() != ''
        self._convert_btn.setText(
            tr('btn_converting') if is_converting else tr('btn_convert')
        )
        self._convert_btn.setToolTip(tr('tt_convert'))
        self._export_btn.setText(tr('btn_export'))
        self._export_btn.setToolTip(tr('tt_export'))

    def _retranslate_preset_combo(self) -> None:
        self._preset.blockSignals(True)
        current_key = self._preset_key
        self._preset.clear()
        for key in _PRESET_KEYS:
            self._preset.addItem(tr(_PRESET_TR[key]))
        self._preset.addItem(tr('custom_preset'))
        if current_key == _CUSTOM_KEY:
            self._preset.setCurrentIndex(len(_PRESET_KEYS))
        elif current_key in _PRESET_KEYS:
            self._preset.setCurrentIndex(_PRESET_KEYS.index(current_key))
        self._preset.blockSignals(False)

    @staticmethod
    def _retranslate_combo(combo: QComboBox, items: list[str], tooltip: str) -> None:
        idx = combo.currentIndex()
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(items)
        combo.setCurrentIndex(max(0, idx))
        combo.setToolTip(tooltip)
        combo.blockSignals(False)

    # ── slots ────────────────────────────────────────────────────────────────────

    def _on_preset(self, idx: int) -> None:
        if idx == len(_PRESET_KEYS):  # Custom
            self._preset_key = _CUSTOM_KEY
            return
        if 0 <= idx < len(_PRESET_KEYS):
            self._preset_key = _PRESET_KEYS[idx]
            s = PRESETS[self._preset_key]
            self._load_settings(s)
            self._settings = s
            self.settings_changed.emit(s)

    def _on_manual_change(self, _=None) -> None:
        self._preset_key = _CUSTOM_KEY
        self._preset.blockSignals(True)
        self._preset.setCurrentIndex(len(_PRESET_KEYS))
        self._preset.blockSignals(False)
        self._settings = self._read()
        self.settings_changed.emit(self._settings)

    def _load_settings(self, s: ConversionSettings) -> None:
        for combo in (self._colormode, self._hierarchical, self._mode_combo):
            combo.blockSignals(True)
        self._colormode.setCurrentIndex(0 if s.colormode == 'color' else 1)
        self._hierarchical.setCurrentIndex(0 if s.hierarchical == 'stacked' else 1)
        self._mode_combo.setCurrentIndex({'spline': 0, 'polygon': 1, 'none': 2}[s.mode])
        for combo in (self._colormode, self._hierarchical, self._mode_combo):
            combo.blockSignals(False)
        self._sl_color_precision.set_value(s.color_precision)
        self._sl_layer_difference.set_value(s.layer_difference)
        self._sl_filter_speckle.set_value(s.filter_speckle)
        self._sl_corner_threshold.set_value(s.corner_threshold)
        self._sl_length_threshold.set_value(s.length_threshold)
        self._sl_contrast.set_value(s.contrast)
        self._sl_saturation.set_value(s.saturation)
        self._sl_sharpness.set_value(s.sharpness)

    def _read(self) -> ConversionSettings:
        modes = ['spline', 'polygon', 'none']
        return ConversionSettings(
            colormode='color' if self._colormode.currentIndex() == 0 else 'binary',
            hierarchical='stacked' if self._hierarchical.currentIndex() == 0 else 'cutout',
            mode=modes[self._mode_combo.currentIndex()],
            filter_speckle=int(self._sl_filter_speckle.value()),
            color_precision=int(self._sl_color_precision.value()),
            layer_difference=int(self._sl_layer_difference.value()),
            corner_threshold=int(self._sl_corner_threshold.value()),
            length_threshold=self._sl_length_threshold.value(),
            contrast=self._sl_contrast.value(),
            saturation=self._sl_saturation.value(),
            sharpness=self._sl_sharpness.value(),
        )

    # ── public API ───────────────────────────────────────────────────────────────

    def settings(self) -> ConversionSettings:
        return self._settings

    def enable_convert(self, enabled: bool) -> None:
        self._convert_btn.setEnabled(enabled)
        self._convert_btn.setText(
            tr('btn_convert') if enabled else tr('btn_converting')
        )

    def enable_export(self, enabled: bool) -> None:
        self._export_btn.setEnabled(enabled)
