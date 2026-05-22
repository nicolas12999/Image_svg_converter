from .translations import TRANSLATIONS

_lang = 'es'


def tr(key: str) -> str:
    """Return the translated string for *key* in the current language."""
    return TRANSLATIONS.get(_lang, TRANSLATIONS['es']).get(key, key)


def set_language(lang: str) -> None:
    global _lang
    if lang in TRANSLATIONS:
        _lang = lang


def current_language() -> str:
    return _lang
