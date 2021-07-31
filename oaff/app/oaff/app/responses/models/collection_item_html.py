from typing import Dict, List

from pydantic import BaseModel

from oaff.app.responses.models.link import Link


class CollectionItemHtml(BaseModel):
    collection_id: str
    feature_id: str
    format_links: List[Link]
    properties: Dict[str, str]
