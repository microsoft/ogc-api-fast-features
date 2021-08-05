from datetime import datetime, tzinfo
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from pygeofilter.ast import (
    And,
    Attribute,
    BBox,
    IsNull,
    Node,
    Or,
    TimeAfter,
    TimeBefore,
    TimeEquals,
)
from pyproj import Transformer

from oaff.app import settings
from oaff.app.configuration.data import get_data_source, get_layer
from oaff.app.configuration.frontend_interface import get_frontend_configuration
from oaff.app.data.sources.common.data_source import DataSource
from oaff.app.data.sources.common.layer import Layer
from oaff.app.data.sources.common.temporal import TemporalInstant, TemporalRange
from oaff.app.i18n.translations import gettext_for_locale
from oaff.app.request_handlers.common.request_handler import RequestHandler
from oaff.app.requests.collection_items import CollectionItems
from oaff.app.responses.models.link import Link, PageLinkRel
from oaff.app.responses.response import Response
from oaff.app.responses.response_format import ResponseFormat


class CollectionsItems(RequestHandler):
    @classmethod
    def type_name(cls) -> str:
        return CollectionItems.__name__

    async def handle(self, request: CollectionItems) -> Type[Response]:
        layer = get_layer(request.collection_id)
        if layer is None:
            return self.collection_404(request.collection_id)
        data_source = get_data_source(layer.data_source_id)
        feature_set_provider = await data_source.get_feature_set_provider(
            layer,
            request.get_item_constraints(),
            self._collect_ast(
                await self._spatial_bounds_to_node(
                    request.spatial_bounds,
                    request.spatial_bounds_crs,
                    data_source,
                    layer,
                )
                if request.spatial_bounds is not None
                else None,
                await self._datetime_to_node(
                    request.temporal_bounds,
                    layer,
                )
                if request.temporal_bounds is not None
                else None,
            ),
        )
        if request.format == ResponseFormat.json:
            return self.raw_to_response(
                await feature_set_provider.as_geojson(
                    self.get_links_for_self(request),
                    self._get_page_link_retriever(request),
                ),
                request,
            )
        elif request.format == ResponseFormat.html:
            response_data = await feature_set_provider.as_html_compatible(
                self.get_links_for_self(request),
                self._get_page_link_retriever(request),
            )
            return self.object_to_response(
                response_data,
                request,
            )

    def _get_page_link_retriever(
        self, request: CollectionItems
    ) -> Callable[[int, int], Dict[PageLinkRel, Link]]:

        frontend_config = get_frontend_configuration()

        def retriever(total_count: int, result_count: int) -> List[Link]:
            links = {}
            if request.offset > 0:
                links[PageLinkRel.PREV] = Link(
                    href=frontend_config.prev_page_link_generator(request.url),
                    rel=PageLinkRel.PREV.value,
                    type=request.format[request.type],
                    title=gettext_for_locale(request.locale)("Previous Page"),
                )
            if (total_count - result_count) > request.offset:
                links[PageLinkRel.NEXT] = Link(
                    href=frontend_config.next_page_link_generator(request.url),
                    rel=PageLinkRel.NEXT.value,
                    type=request.format[request.type],
                    title=gettext_for_locale(request.locale)("Next Page"),
                )

            return links

        return retriever

    def _collect_ast(
        self,
        bbox: BBox,
        datetime: Any,
    ) -> Type[Node]:
        if bbox is None and datetime is None:
            return None
        else:
            if bbox is not None and datetime is not None:
                return And(lhs=bbox, rhs=datetime)
            elif bbox is None:
                return datetime
            else:
                return bbox

    async def _spatial_bounds_to_node(
        self,
        spatial_bounds: Optional[
            Union[
                Tuple[float, float, float, float],
                Tuple[float, float, float, float, float, float],
            ]
        ],
        spatial_bounds_crs: str,
        data_source: DataSource,
        layer: Layer,
    ) -> BBox:
        x_min, y_min, x_max, y_max = (
            spatial_bounds
            if len(spatial_bounds) == 4
            else (spatial_bounds[i] for i in [0, 1, 3, 4])
        )
        transformer = Transformer.from_crs(
            "EPSG:4326",  # True until Features API spec part 2 is implemented
            f"{layer.geometry_crs_auth_name}:{layer.geometry_crs_auth_code}",
            always_xy=True,
        )
        ll = transformer.transform(x_min, y_min)
        ur = transformer.transform(x_max, y_max)
        return BBox(
            lhs=Attribute(settings.SPATIAL_FILTER_GEOMETRY_FIELD_ALIAS),
            minx=ll[0],
            miny=ll[1],
            maxx=ur[0],
            maxy=ur[1],
            crs=await data_source.get_crs_identifier(layer),
        )

    async def _datetime_to_node(  # noqa: C901
        self,
        temporal_bounds: Union[Tuple[datetime], Tuple[datetime, datetime]],
        layer: Layer,
    ) -> Type[Node]:
        if len(list(filter(lambda bound: bound is not None, temporal_bounds))) == 0:
            return None
        nodes = []
        for data_field in layer.temporal_attributes:
            if len(temporal_bounds) == 2:
                query_start, query_end = temporal_bounds
                if data_field.__class__ is TemporalInstant:
                    if query_start is not None and query_end is not None:
                        nodes.append(
                            And(
                                lhs=TimeBefore(
                                    lhs=Attribute(data_field.field_name),
                                    rhs=self._match_query_time_to_instant_field(
                                        query_end, data_field
                                    ),
                                ),
                                rhs=TimeAfter(
                                    lhs=Attribute(data_field.field_name),
                                    rhs=self._match_query_time_to_instant_field(
                                        query_start, data_field
                                    ),
                                ),
                            )
                        )
                    elif query_start is not None:
                        nodes.append(
                            TimeAfter(
                                lhs=Attribute(data_field.field_name),
                                rhs=self._match_query_time_to_instant_field(
                                    query_start, data_field
                                ),
                            )
                        )
                    elif query_end is not None:
                        nodes.append(
                            TimeBefore(
                                lhs=Attribute(data_field.field_name),
                                rhs=self._match_query_time_to_instant_field(
                                    query_end, data_field
                                ),
                            )
                        )
                elif data_field.__class__ is TemporalRange:

                    def get_data_start_precedes_query_end():
                        return Or(
                            lhs=IsNull(
                                lhs=Attribute(data_field.start_field_name),
                                not_=False,
                            ),
                            rhs=TimeBefore(
                                lhs=Attribute(data_field.start_field_name),
                                rhs=self._match_query_time_to_start_field(
                                    query_end, data_field
                                ),
                            ),
                        )

                    def get_data_end_succeeds_query_start():
                        return Or(
                            lhs=IsNull(
                                lhs=Attribute(data_field.end_field_name),
                                not_=False,
                            ),
                            rhs=TimeAfter(
                                lhs=Attribute(data_field.end_field_name),
                                rhs=self._match_query_time_to_end_field(
                                    query_start, data_field
                                ),
                            ),
                        )

                    if query_start is not None and query_end is not None:
                        nodes.append(
                            And(
                                lhs=get_data_start_precedes_query_end(),
                                rhs=get_data_end_succeeds_query_start(),
                            )
                        )
                    elif query_start is not None:
                        nodes.append(get_data_end_succeeds_query_start())
                    elif query_end is not None:
                        nodes.append(get_data_start_precedes_query_end())

            elif len(temporal_bounds) == 1:
                query_instant = temporal_bounds[0]
                if data_field.__class__ is TemporalInstant:

                    nodes.append(
                        TimeEquals(
                            lhs=Attribute(data_field.field_name),
                            rhs=self._match_query_time_to_instant_field(
                                query_instant, data_field
                            ),
                        )
                    )
                elif data_field.__class__ is TemporalRange:
                    unbounded_end = And(
                        lhs=IsNull(
                            lhs=Attribute(data_field.end_field_name),
                            not_=False,
                        ),
                        rhs=TimeAfter(
                            lhs=self._match_query_time_to_start_field(
                                query_instant, data_field
                            ),
                            rhs=Attribute(data_field.start_field_name),
                        ),
                    )
                    unbounded_start = And(
                        lhs=IsNull(
                            lhs=Attribute(data_field.start_field_name),
                            not_=False,
                        ),
                        rhs=TimeBefore(
                            lhs=self._match_query_time_to_end_field(
                                query_instant, data_field
                            ),
                            rhs=Attribute(data_field.end_field_name),
                        ),
                    )
                    bounded = And(
                        lhs=TimeAfter(
                            lhs=self._match_query_time_to_start_field(
                                query_instant, data_field
                            ),
                            rhs=Attribute(data_field.start_field_name),
                        ),
                        rhs=TimeBefore(
                            lhs=self._match_query_time_to_end_field(
                                query_instant, data_field
                            ),
                            rhs=Attribute(data_field.end_field_name),
                        ),
                    )
                    nodes.append(
                        Or(
                            lhs=Or(
                                lhs=unbounded_start,
                                rhs=unbounded_end,
                            ),
                            rhs=bounded,
                        )
                    )

        if len(nodes) == 1:
            return nodes[0]
        elif len(nodes) > 1:
            combined = nodes.pop()
            while len(nodes) > 0:
                combined = Or(lhs=combined, rhs=nodes.pop())
            return combined
        else:
            return None

    def _match_query_time_to_instant_field(
        self, query_time: datetime, data_field: TemporalInstant
    ) -> datetime:
        return self._match_query_time_to(
            query_time, data_field.field_tz_aware, data_field.tz
        )

    def _match_query_time_to_start_field(
        self, query_time: datetime, range_fields: TemporalRange
    ) -> datetime:
        return self._match_query_time_to(
            query_time, range_fields.start_tz_aware, range_fields.tz
        )

    def _match_query_time_to_end_field(
        self, query_time: datetime, range_fields: TemporalRange
    ) -> datetime:
        return self._match_query_time_to(
            query_time, range_fields.end_tz_aware, range_fields.tz
        )

    def _match_query_time_to(
        self, query_time: datetime, tz_aware: bool, tz: Type[tzinfo]
    ) -> datetime:
        return query_time if tz_aware else query_time.astimezone(tz).replace(tzinfo=None)
