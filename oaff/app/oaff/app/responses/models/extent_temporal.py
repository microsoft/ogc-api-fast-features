from typing import List, Optional

from pydantic import BaseModel, validator


class ExtentTemporal(BaseModel):
    interval: List[List[Optional[str]]]

    @validator("interval")
    def _pairs_only(cls, value):
        for entry in value:
            if len(entry) != 2:
                raise ValueError(
                    "".join(
                        [
                            "Temporal intervals must be described in pairs; ",
                            "use 'null' to indicate an open-ended interval",
                        ]
                    )
                )
        return value
