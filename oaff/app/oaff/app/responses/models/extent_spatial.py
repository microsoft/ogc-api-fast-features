from typing import List

from pydantic import BaseModel, validator

from oaff.app.util import LAT_MAX, LAT_MIN, LON_MAX, LON_MIN, is_valid_lat, is_valid_lon


class ExtentSpatial(BaseModel):
    bbox: List[List[float]]

    @validator("bbox")
    def _bbox_valid(cls, value):
        for each_bbox in value:
            if len(each_bbox) != 4:
                raise ValueError(
                    f"bbox must have exactly four entries (currently {len(each_bbox)})"
                )
            if not (
                is_valid_lon(each_bbox[0])
                and is_valid_lat(each_bbox[1])
                and is_valid_lon(each_bbox[2])
                and is_valid_lat(each_bbox[3])
            ):
                raise ValueError(
                    "".join(
                        [
                            f"{each_bbox[0]} and {each_bbox[2]} ",
                            f"must not exceed {LON_MIN} and {LON_MAX}. "
                            f"{each_bbox[1]} and {each_bbox[3]} ",
                            f"must not exceed {LAT_MIN} and {LAT_MAX}.",
                        ]
                    )
                )
        return value
