
from typing import List, Optional, Dict, Any
from instance_dao import InstanceDAO
from model import Instance


class InstanceService:
    def __init__(self, dao: InstanceDAO):
        self.dao = dao
    
    def get_instances(
        self, 
        page: int = 1, 
        page_size: int = 10,
        user_id: Optional[int] = None,
        role_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get instances with pagination and filtering
        
        Args:
            page: Page number (starts from 1)
            page_size: Number of items per page
            user_id: Filter by user ID
            role_id: Filter by instance role ID  
            name: Filter by instance name (IP address)
            
        Returns:
            Dictionary containing instances data and pagination info
        """
        # Start with all instances
        instances = self.dao.get_all()
        
        # Apply filters
        if user_id is not None:
            instances = [inst for inst in instances if inst.manager.id == user_id]
        
        if role_id is not None:
            instances = [inst for inst in instances if inst.instance_role.id == role_id]
        
        if name is not None and name.strip():
            name_lower = name.strip().lower()
            instances = [inst for inst in instances if name_lower in inst.name.lower()]
        
        # Calculate pagination
        total = len(instances)
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        
        # Get paginated results
        paginated_instances = instances[offset:offset + page_size]
        
        return {
            "data": paginated_instances,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "user_id": user_id,
                "role_id": role_id,
                "name": name
            }
        }
    
    def get_instance_by_id(self, instance_id: int) -> Optional[Instance]:
        """Get a specific instance by ID"""
        return self.dao.get_by_id(instance_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about instances"""
        instances = self.dao.get_all()
        total = len(instances)
        
        if total == 0:
            return {
                "total": 0,
                "gpu_servers": 0,
                "non_gpu_servers": 0,
                "os_distribution": {},
                "role_distribution": {},
                "manager_distribution": {}
            }
        
        # Count by OS type
        os_stats = {}
        for instance in instances:
            os_name = instance.os.display
            os_stats[os_name] = os_stats.get(os_name, 0) + 1
        
        # Count by instance role
        role_stats = {}
        for instance in instances:
            role_name = instance.instance_role.name
            role_stats[role_name] = role_stats.get(role_name, 0) + 1
        
        # Count GPU servers
        gpu_servers = len([inst for inst in instances if inst.is_gpu_server])
        
        # Count by manager
        manager_stats = {}
        for instance in instances:
            manager_name = f"{instance.manager.first_name} {instance.manager.last_name}"
            manager_stats[manager_name] = manager_stats.get(manager_name, 0) + 1
        
        return {
            "total": total,
            "gpu_servers": gpu_servers,
            "non_gpu_servers": total - gpu_servers,
            "os_distribution": os_stats,
            "role_distribution": role_stats,
            "manager_distribution": manager_stats
        }