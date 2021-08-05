from sqlalchemy.sql.schema import Table

from oaff.app.data.sources.common.layer import Layer


class PostgresqlLayer(Layer):
    schema_name: str
    table_name: str
    geometry_field_name: str
    geometry_srid: int
    model: Table

    class Config:
        arbitrary_types_allowed = True

    @property
    def unique_field_name(self):
        # layers are only available if they have exactly one PK
        return self.model.primary_key.columns.keys()[0]

    @property
    def fields(self):
        return self.model.columns.keys()
