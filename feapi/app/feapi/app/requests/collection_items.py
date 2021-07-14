from feapi.app.data.retrieval.filter_parameters import FilterParameters
from feapi.app.data.retrieval.item_constraints import ItemConstraints
from feapi.app.requests.common.request_type import RequestType


class CollectionItems(RequestType, ItemConstraints, FilterParameters):
    collection_id: str

    def get_item_constraints(self) -> ItemConstraints:
        return ItemConstraints(
            limit=self.limit,
            offset=self.offset,
        )
