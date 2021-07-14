from gettext import translation
from os import path
from typing import Any, Callable, Final

from feapi.app.i18n.locales import Locales

DEFAULT_LOCALE: Final = Locales.en_US
_TRANSLATIONS: Final = {
    locale.value: translation(
        domain="translations",
        localedir=path.join(path.dirname(__file__), "locale"),
        languages=[locale.name],
    )
    for locale in Locales
}


def get_translations_for_locale(locale: Locales) -> Any:
    return (
        _TRANSLATIONS[locale.value]
        if locale.value in _TRANSLATIONS
        else _TRANSLATIONS[DEFAULT_LOCALE]
    )


def gettext_for_locale(locale: Locales) -> Callable[[str], str]:
    return get_translations_for_locale(locale).gettext
