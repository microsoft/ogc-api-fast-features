import re
from enum import Enum

from pydantic import BaseModel, validator


class LinkRel(str, Enum):
    SELF = "self"
    ALTERNATE = "alternate"
    DESCRIBED_BY = "describedby"
    ENCLOSURE = "enclosure"
    ITEMS = "items"
    NEXT = "next"
    PREV = "prev"
    COLLECTION = "collection"
    SERVICE_DESC = "service-desc"
    SERVICE_DOC = "service-doc"
    CONFORMANCE = "conformance"
    DATA = "data"


class PageLinkRel(str, Enum):
    NEXT = LinkRel.NEXT.value
    PREV = LinkRel.PREV.value


class Link(BaseModel):
    href: str
    rel: LinkRel
    type: str
    title: str

    @validator("type")
    def _type_is_mime(cls, value):
        if re.match(r"^\w+/[-.\w]+(?:\+[-.\w]+)?", value) is not None:
            return value
        raise ValueError(f"{value} is not recognised as a MIME type")

    def jsonable(self):
        return dict(self)
