from typing import Final

from oaff.app.responses.response_format import ResponseFormat
from oaff.fastapi.api.util import alternate_format_for_url

input_url_template: Final = "https://test.url/with/endpoint{0}"


def test_alternate_format_without_parameter():
    for end in ["", "/"]:
        for format in ResponseFormat:
            assert alternate_format_for_url(
                input_url_template.format(end), format
            ) == input_url_template.format(f"{end}?format={format.name}")


def test_alternate_format_without_parameter_end_slash():
    for end in ["", "/"]:
        for current_format in ResponseFormat:
            for target_format in [
                target_format
                for target_format in ResponseFormat
                if target_format != current_format
            ]:
                assert (
                    alternate_format_for_url(
                        input_url_template.format(f"{end}?format={current_format.name}"),
                        target_format,
                    )
                    == input_url_template.format(f"{end}?format={target_format.name}")
                )
