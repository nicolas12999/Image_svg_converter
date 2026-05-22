# Catppuccin Mocha (dark) and Catppuccin Latte (light) palettes

THEME_COLORS = {
    'dark': {
        'drop_border': '#45475a',
        'drop_border_hover': '#89b4fa',
        'drop_bg': '#181825',
        'drop_bg_hover': '#1e1e2e',
        'pane_bg': '#11111b',
        'pane_title': '#6c7086',
        'icon': '#cdd6f4',        # matches secondary button text in dark mode
    },
    'light': {
        'drop_border': '#bcc0cc',
        'drop_border_hover': '#1e66f5',
        'drop_bg': '#dce0e8',
        'drop_bg_hover': '#e6e9ef',
        'pane_bg': '#dce0e8',
        'pane_title': '#8c8fa1',
        'icon': '#4c4f69',        # matches secondary button text in light mode
    },
}

DARK = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-size: 13px;
}
QLabel {
    color: #cdd6f4;
    background: transparent;
}
QLabel#heading {
    color: #89b4fa;
    font-size: 15px;
    font-weight: bold;
}
QLabel#section {
    color: #6c7086;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    padding-top: 6px;
}
QLabel#value {
    color: #89b4fa;
    font-family: monospace;
    min-width: 40px;
    background: transparent;
}
QLabel#placeholder {
    color: #45475a;
    font-size: 13px;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:pressed {
    background-color: #74c7ec;
}
QPushButton:disabled {
    background-color: #313244;
    color: #585b70;
}
QPushButton#secondary {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    font-weight: normal;
}
QPushButton#secondary:hover {
    background-color: #45475a;
    border-color: #585b70;
}
QPushButton#secondary:pressed {
    background-color: #585b70;
}
QPushButton#secondary:disabled {
    background-color: #181825;
    color: #45475a;
    border-color: #313244;
}
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px 10px;
    color: #cdd6f4;
}
QComboBox:focus {
    border-color: #89b4fa;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
    color: #cdd6f4;
    outline: none;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #313244;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #89b4fa;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #b4befe;
}
QSlider::sub-page:horizontal {
    background: #89b4fa;
    border-radius: 2px;
}
QFrame#divider {
    color: #313244;
    max-height: 1px;
    background-color: #313244;
}
QScrollArea {
    border: none;
    background-color: #11111b;
}
QScrollArea > QWidget > QWidget {
    background-color: #11111b;
}
QScrollBar:vertical {
    background: #181825;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #181825;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover {
    background: #585b70;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}
QSplitter::handle {
    background: #313244;
}
QStatusBar {
    background-color: #181825;
    color: #6c7086;
    font-size: 12px;
}
QStatusBar QLabel {
    color: #6c7086;
}
QMessageBox {
    background-color: #1e1e2e;
}
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 4px 6px;
    border-radius: 4px;
}
"""

LIGHT = """
QMainWindow, QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-size: 13px;
}
QLabel {
    color: #4c4f69;
    background: transparent;
}
QLabel#heading {
    color: #1e66f5;
    font-size: 15px;
    font-weight: bold;
}
QLabel#section {
    color: #9ca0b0;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    padding-top: 6px;
}
QLabel#value {
    color: #1e66f5;
    font-family: monospace;
    min-width: 40px;
    background: transparent;
}
QLabel#placeholder {
    color: #bcc0cc;
    font-size: 13px;
}
QPushButton {
    background-color: #1e66f5;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #7287fd;
}
QPushButton:pressed {
    background-color: #04a5e5;
}
QPushButton:disabled {
    background-color: #ccd0da;
    color: #9ca0b0;
}
QPushButton#secondary {
    background-color: #ccd0da;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    font-weight: normal;
}
QPushButton#secondary:hover {
    background-color: #bcc0cc;
    border-color: #acb0be;
}
QPushButton#secondary:pressed {
    background-color: #acb0be;
}
QPushButton#secondary:disabled {
    background-color: #e6e9ef;
    color: #bcc0cc;
    border-color: #ccd0da;
}
QComboBox {
    background-color: #e6e9ef;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    padding: 5px 10px;
    color: #4c4f69;
}
QComboBox:focus {
    border-color: #1e66f5;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #e6e9ef;
    border: 1px solid #bcc0cc;
    selection-background-color: #ccd0da;
    color: #4c4f69;
    outline: none;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #ccd0da;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #1e66f5;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #7287fd;
}
QSlider::sub-page:horizontal {
    background: #1e66f5;
    border-radius: 2px;
}
QFrame#divider {
    color: #ccd0da;
    max-height: 1px;
    background-color: #ccd0da;
}
QScrollArea {
    border: none;
    background-color: #dce0e8;
}
QScrollArea > QWidget > QWidget {
    background-color: #dce0e8;
}
QScrollBar:vertical {
    background: #e6e9ef;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #bcc0cc;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #acb0be;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #e6e9ef;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #bcc0cc;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover {
    background: #acb0be;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}
QSplitter::handle {
    background: #ccd0da;
}
QStatusBar {
    background-color: #dce0e8;
    color: #8c8fa1;
    font-size: 12px;
}
QStatusBar QLabel {
    color: #8c8fa1;
}
QMessageBox {
    background-color: #eff1f5;
}
QToolTip {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    padding: 4px 6px;
    border-radius: 4px;
}
"""

STYLESHEETS = {'dark': DARK, 'light': LIGHT}
