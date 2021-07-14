from pydantic import BaseModel

from feapi.app.data.sources.common.layer import Layer
from feapi.app.responses.models.extent_spatial import ExtentSpatial
from feapi.app.responses.models.extent_temporal import ExtentTemporal


class Extent(BaseModel):
    spatial: ExtentSpatial
    temporal: ExtentTemporal

    @classmethod
    def has_extent(cls, layer: Layer):
        return layer.bboxes is not None and layer.intervals is not None

    @classmethod
    def from_layer(cls, layer: Layer):
        return cls(
            spatial=ExtentSpatial(
                bbox=layer.bboxes,
            ),
            temporal=ExtentTemporal(interval=layer.intervals),
        )

    def jsonable(self):
        return {
            "spatial": dict(self.spatial),
            "temporal": dict(self.temporal),
        }
