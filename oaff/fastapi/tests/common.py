from datetime import datetime
from typing import List, Type

from oaff.app.requests.common.request_type import RequestType
from oaff.app.responses.data_response import DataResponse
from oaff.app.responses.response_format import ResponseFormat
from oaff.app.responses.response_type import ResponseType


def get_mock_handler_provider(handler_calls: List[Type[RequestType]]):
    def mock_handler_provider():
        async def mock_handler(request):
            handler_calls.append(request)
            return DataResponse(
                mime_type=ResponseFormat.json[ResponseType.METADATA],
                encoded_response="",
            )

        return mock_handler

    return mock_handler_provider


def get_valid_datetime_parameter() -> str:
    return datetime.utcnow().isoformat("T") + "Z"
