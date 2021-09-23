from os import path

from jinja2 import Environment, PackageLoader, select_autoescape

from oaff.app.configuration.frontend_interface import get_frontend_configuration
from oaff.app.i18n.locales import Locales
from oaff.app.i18n.translations import get_translations_for_locale


def get_rendered_html(template_name: str, data: object, locale: Locales) -> str:
    env = Environment(
        extensions=["jinja2.ext.i18n"],
        loader=PackageLoader("oaff.app", path.join("responses", "templates", "html")),
        autoescape=select_autoescape(["html"]),
    )
    env.install_gettext_translations(get_translations_for_locale(locale))  # type: ignore
    frontend_config = get_frontend_configuration()
    return env.get_template(f"{template_name}.jinja2").render(
        response=data,
        api_url_base=frontend_config.api_url_base,
        asset_url_base=frontend_config.asset_url_base,
    )
