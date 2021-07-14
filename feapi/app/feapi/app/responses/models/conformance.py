from typing import List

from pydantic import BaseModel

from feapi.app.responses.models.link import Link


class Conformance(BaseModel):
    conformsTo: List[str]

    def jsonable(self):
        return dict(self)


class ConformanceHtml(Conformance):
    format_links: List[Link]


class ConformanceJson(Conformance):
    pass
