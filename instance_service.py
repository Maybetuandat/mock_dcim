
from typing import List, Optional, Dict, Any
from instance_dao import InstanceDAO
from model import Instance, InstanceRole


class InstanceService:
    def __init__(self, dao: InstanceDAO):
        self.dao = dao
    
    def get_instances(
        self, 
        page: int = 1, 
        page_size: int = 10,
        user_id: Optional[str] = None,
        instance_role_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        instances = self.dao.get_all()


        if user_id is not None:
            instances = [inst for inst in instances if inst.manager.id == user_id]

        if instance_role_id is not None:
            instances = [inst for inst in instances if inst.instance_role.id == instance_role_id]

        if name is not None and name.strip():
            name_lower = name.strip().lower()
            instances = [inst for inst in instances if name_lower in inst.name.lower()]
        
       
        total = len(instances)
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size

        paginated_instances = instances[offset:offset + page_size]
        
        return {
            "instances": paginated_instances,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "filters": {
                "user_id": user_id,
                "instance_role_id": instance_role_id,
                "name": name
            }
        }

    def get_instance_roles(self) -> List[InstanceRole]:
            instances = self.dao.get_all()
            roles = {inst.instance_role.id: inst.instance_role for inst in instances}
            return list(roles.values())