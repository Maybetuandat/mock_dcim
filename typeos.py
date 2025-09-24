from pydantic import BaseModel


class TypeOs(BaseModel):
    value: int
    label:str