from typing import List

from pydantic import BaseModel

from oaff.app.responses.models.link import Link


class Landing(BaseModel):
    title: str
    description: str


class LandingJson(Landing):
    links: List[Link]

    def jsonable(self):
        return {
            **dict(self),
            **{
                "links": [link.jsonable() for link in self.links],
            },
        }


class LandingHtml(Landing):
    format_links: List[Link]
    openapi_links: List[Link]
    collection_links: List[Link]
    conformance_links: List[Link]
