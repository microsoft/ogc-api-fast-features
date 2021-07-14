from pydantic import BaseModel


class ItemConstraints(BaseModel):
    limit: int
    offset: int
