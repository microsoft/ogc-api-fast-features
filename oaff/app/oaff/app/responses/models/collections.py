from typing import List

from pydantic import BaseModel

from oaff.app.responses.models.collection import CollectionHtml, CollectionJson
from oaff.app.responses.models.link import Link


class CollectionsHtml(BaseModel):
    collections: List[CollectionHtml]
    format_links: List[Link]


class CollectionsJson(BaseModel):
    collections: List[CollectionJson]
    links: List[Link]

    def jsonable(self):
        return {
            "collections": [collection.jsonable() for collection in self.collections],
            "links": [dict(link) for link in self.links],
        }
