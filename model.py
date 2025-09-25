
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str


class Os(BaseModel):
    id: int
    name: str
    type: int
    display: str


class TypeOs(BaseModel):
    value: int
    label: str


class InstanceRole(BaseModel):
    id: int
    name: str 
    slug: str


class Instance(BaseModel):
    uid: str
    id: int
    name: str  # this is ip address
    manager: User
    type: TypeOs
    os: Os
    is_gpu_server: bool
    instance_role: InstanceRole
    created_at: datetime
    updated_at: datetime