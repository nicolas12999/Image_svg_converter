from PySide6.QtCore import QObject, Signal

from app.i18n import set_language


class _AppSettings(QObject):
    language_changed = Signal(str)  # emits lang code: 'es' | 'en' | 'zh'
    theme_changed = Signal(str)     # emits theme name: 'dark' | 'light'

    def __init__(self) -> None:
        super().__init__()
        self._language = 'es'
        self._theme = 'dark'

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, lang: str) -> None:
        if lang != self._language:
            self._language = lang
            set_language(lang)
            self.language_changed.emit(lang)

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, t: str) -> None:
        if t != self._theme:
            self._theme = t
            self.theme_changed.emit(t)


# Lazy singleton — created on first access so QApplication is always ready first.
_instance: _AppSettings | None = None


def get_app_settings() -> _AppSettings:
    global _instance
    if _instance is None:
        _instance = _AppSettings()
    return _instance
