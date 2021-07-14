from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from feapi.app.responses.models.link import Link


class CollectionItemsHtml(BaseModel):
    format_links: List[Link]
    next_link: Optional[Link]
    prev_link: Optional[Link]
    features: List[Dict[str, Any]]
    collection_id: str
    unique_field_name: str

    def has_features(self) -> bool:
        return len(self.features) > 0

    def field_names(self) -> List[str]:
        return (
            [self.unique_field_name]
            + sorted(
                [
                    field_name
                    for field_name in self.features[0].keys()
                    if field_name != self.unique_field_name
                ]
            )
            if self.has_features()
            else []
        )
