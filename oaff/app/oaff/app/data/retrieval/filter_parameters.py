from datetime import datetime
from typing import Optional, Tuple, Union

from pydantic import BaseModel


class FilterParameters(BaseModel):
    spatial_bounds: Optional[
        Union[
            Tuple[float, float, float, float],
            Tuple[float, float, float, float, float, float],
        ]
    ]
    spatial_bounds_crs: Optional[str]
    temporal_bounds: Optional[
        Union[Tuple[Optional[datetime], Optional[datetime]], Tuple[datetime]]
    ]
    filter_cql: Optional[str]
    filter_lang: Optional[str]
    filter_crs: Optional[str]
