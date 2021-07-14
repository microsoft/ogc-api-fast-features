from typing import List, Optional

from pydantic import BaseModel


class Provider(BaseModel):
    url: str
    name: str
    roles: Optional[List[str]] = None
