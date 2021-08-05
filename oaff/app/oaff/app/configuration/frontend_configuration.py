from typing import Callable

from pydantic import BaseModel

from oaff.app.responses.response_format import ResponseFormat


class FrontendConfiguration(BaseModel):
    asset_url_base: str
    api_url_base: str
    endpoint_format_switcher: Callable[[str, ResponseFormat], str]
    next_page_link_generator: Callable[[str], str]
    prev_page_link_generator: Callable[[str], str]
    openapi_path_html: str
    openapi_path_json: str

    def get_items_path(self, layer_id: str) -> str:
        return f"{self.api_url_base}/collections/{layer_id}/items"

    def get_collection_path(self, layer_id: str) -> str:
        return f"{self.api_url_base}/collections/{layer_id}"
