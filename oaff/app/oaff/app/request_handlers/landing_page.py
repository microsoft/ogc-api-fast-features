from typing import Type

from oaff.app.configuration.frontend_interface import get_frontend_configuration
from oaff.app.i18n.translations import gettext_for_locale
from oaff.app.request_handlers.common.request_handler import RequestHandler
from oaff.app.requests.landing_page import LandingPage
from oaff.app.responses.models.landing import LandingHtml, LandingJson
from oaff.app.responses.models.link import Link, LinkRel
from oaff.app.responses.response import Response
from oaff.app.responses.response_format import ResponseFormat
from oaff.app.responses.response_type import ResponseType
from oaff.app.settings import OPENAPI_OGC_TYPE


class LandingPage(RequestHandler):
    @classmethod
    def type_name(cls) -> str:
        return LandingPage.__name__

    async def handle(self, request: LandingPage) -> Type[Response]:
        gettext = gettext_for_locale(request.locale)
        frontend = get_frontend_configuration()
        title = gettext("Features API Landing Page")
        description = ""
        format_links = self.get_links_for_self(request)
        openapi_links = [
            Link(
                href=f"{request.root}{frontend.openapi_path_html}",
                rel=LinkRel.SERVICE_DOC,
                type="text/html",
                title=gettext("API Definition (%s)" % "text/html"),
            ),
            Link(
                href=f"{request.root}{frontend.openapi_path_json}",
                rel=LinkRel.SERVICE_DESC,
                type=OPENAPI_OGC_TYPE,
                title=gettext("API Definition (%s)" % OPENAPI_OGC_TYPE),
            ),
        ]
        conformance_links = [
            Link(
                href="".join(
                    [
                        f"{request.root}{frontend.api_url_base}/conformance",
                        f"?format={format.name}",
                    ]
                ),
                rel=LinkRel.CONFORMANCE,
                type=format[ResponseType.METADATA],
                title=gettext("Conformance (%s)" % format[ResponseType.METADATA]),
            )
            for format in ResponseFormat
        ]
        collection_links = [
            Link(
                href="".join(
                    [
                        f"{request.root}{frontend.api_url_base}/collections",
                        f"?format={format.name}",
                    ]
                ),
                rel=LinkRel.DATA,
                type=format[ResponseType.METADATA],
                title=gettext("Collections (%s)" % format[ResponseType.METADATA]),
            )
            for format in ResponseFormat
        ]
        if request.format == ResponseFormat.html:
            return self.object_to_html_response(
                LandingHtml(
                    title=title,
                    description=description,
                    format_links=format_links,
                    openapi_links=openapi_links,
                    conformance_links=conformance_links,
                    collection_links=collection_links,
                ),
                request,
            )
        elif request.format == ResponseFormat.json:
            return self.object_to_json_response(
                LandingJson(
                    title=title,
                    description=description,
                    links=format_links
                    + openapi_links
                    + conformance_links
                    + collection_links,
                ),
                request,
            )
