from pydantic import BaseModel


class Os(BaseModel):
    id: int
    name: str
    type: int
    display: str