from typing import List, Optional

from pydantic import BaseModel

from oaff.app.data.sources.common.provider import Provider
from oaff.app.data.sources.common.temporal import TemporalDeclaration


class Layer(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    bboxes: List[List[float]]
    intervals: List[List[Optional[str]]]
    data_source_id: str
    geometry_crs_auth_name: str
    geometry_crs_auth_code: int
    temporal_attributes: List[TemporalDeclaration]
    license: Optional[str] = None
    keywords: Optional[List[str]] = None
    providers: Optional[List[Provider]] = None
