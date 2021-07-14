from feapi.app.requests.common.request_type import RequestType


class Feature(RequestType):
    collection_id: str
    feature_id: str
