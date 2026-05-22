from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QDialog, QDialogButtonBox, QFrame,
    QHBoxLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout, QWidget,
)

from app.core.app_settings import get_app_settings
from app.i18n import tr


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumWidth(320)
        self._build_ui()
        self.retranslate_ui()

        cfg = get_app_settings()
        cfg.language_changed.connect(self.retranslate_ui)

    # ── build ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        cfg = get_app_settings()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 20)

        # ── Language ─────────────────────────────────────────────────────────────
        self._lang_heading = QLabel()
        self._lang_heading.setObjectName("section")
        layout.addWidget(self._lang_heading)

        lang_row = QHBoxLayout()
        lang_row.setSpacing(8)

        self._btn_es = QRadioButton()
        self._btn_en = QRadioButton()
        self._btn_zh = QRadioButton()

        self._lang_group = QButtonGroup(self)
        for btn, code in ((self._btn_es, 'es'), (self._btn_en, 'en'), (self._btn_zh, 'zh')):
            self._lang_group.addButton(btn)
            lang_row.addWidget(btn)
            if code == cfg.language:
                btn.setChecked(True)

        lang_row.addStretch()
        layout.addLayout(lang_row)

        self._btn_es.toggled.connect(lambda on: on and self._set_lang('es'))
        self._btn_en.toggled.connect(lambda on: on and self._set_lang('en'))
        self._btn_zh.toggled.connect(lambda on: on and self._set_lang('zh'))

        layout.addWidget(self._divider())

        # ── Theme ─────────────────────────────────────────────────────────────────
        self._theme_heading = QLabel()
        self._theme_heading.setObjectName("section")
        layout.addWidget(self._theme_heading)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(8)

        self._btn_dark = QPushButton()
        self._btn_dark.setCheckable(True)
        self._btn_dark.setObjectName("secondary")

        self._btn_light = QPushButton()
        self._btn_light.setCheckable(True)
        self._btn_light.setObjectName("secondary")

        if cfg.theme == 'dark':
            self._btn_dark.setChecked(True)
        else:
            self._btn_light.setChecked(True)

        self._btn_dark.clicked.connect(lambda: self._set_theme('dark'))
        self._btn_light.clicked.connect(lambda: self._set_theme('light'))

        theme_row.addWidget(self._btn_dark)
        theme_row.addWidget(self._btn_light)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        layout.addStretch()
        layout.addWidget(self._divider())

        # ── Close ─────────────────────────────────────────────────────────────────
        self._close_btn = QPushButton()
        self._close_btn.clicked.connect(self.accept)
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_row.addWidget(self._close_btn)
        layout.addLayout(close_row)

    def _divider(self) -> QFrame:
        line = QFrame()
        line.setObjectName("divider")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    # ── actions ──────────────────────────────────────────────────────────────────

    def _set_lang(self, lang: str) -> None:
        get_app_settings().language = lang

    def _set_theme(self, theme: str) -> None:
        cfg = get_app_settings()
        cfg.theme = theme
        # Keep toggle buttons in sync
        self._btn_dark.setChecked(theme == 'dark')
        self._btn_light.setChecked(theme == 'light')

    # ── retranslation ─────────────────────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self.setWindowTitle(tr('settings_title'))
        self._lang_heading.setText(tr('settings_language').upper())
        self._btn_es.setText(tr('lang_es'))
        self._btn_en.setText(tr('lang_en'))
        self._btn_zh.setText(tr('lang_zh'))
        self._theme_heading.setText(tr('settings_theme').upper())
        self._btn_dark.setText(tr('settings_dark'))
        self._btn_light.setText(tr('settings_light'))
        self._close_btn.setText(tr('settings_close'))
