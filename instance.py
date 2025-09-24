import datetime
from pydantic import BaseModel

from User import User
from os import Os

from instance_role import InstanceRole
from typeos import TypeOs
class Instance(BaseModel):
    uid: str
    id: int
    name:str # this is ip address
    manager: User
    type: TypeOs
    os: Os
    is_gpu_server: bool
    instance_role: InstanceRole
    created_at: datetime
    updated_at: datetime