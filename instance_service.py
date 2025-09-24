# services/instance_service.py
from typing import Dict, List, Optional, Tuple
from dao.instance_dao import InstanceDAO
from models.instance import Instance
from models.User import User
from models.instance_role import InstanceRole
from models.typeos import TypeOs


class InstanceService:
    def __init__(self, json_file_path: str = "data.json"):
        self.dao = InstanceDAO(json_file_path)
    
    def get_instances_paginated(
        self, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict:
        """Get instances with pagination metadata"""
        # Validate input parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        skip = (page - 1) * page_size
        
        try:
            instances = self.dao.get_instances(skip=skip, limit=page_size)
            total_count = self.dao.get_total_count()
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                "data": [self._instance_to_dict(instance) for instance in instances],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        except Exception as e:
            raise Exception(f"Error getting instances: {str(e)}")
    
    def search_instances(
        self,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        user_id: Optional[int] = None,
        instance_role_id: Optional[int] = None,
        type_value: Optional[int] = None,
        is_gpu_server: Optional[bool] = None
    ) -> Dict:
        """Search instances with filters and pagination"""
        # Validate input parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        skip = (page - 1) * page_size
        
        try:
            instances, total_count = self.dao.search_instances(
                keyword=keyword,
                user_id=user_id,
                instance_role_id=instance_role_id,
                type_value=type_value,
                is_gpu_server=is_gpu_server,
                skip=skip,
                limit=page_size
            )
            
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                "data": [self._instance_to_dict(instance) for instance in instances],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters": {
                    "keyword": keyword,
                    "user_id": user_id,
                    "instance_role_id": instance_role_id,
                    "type_value": type_value,
                    "is_gpu_server": is_gpu_server
                }
            }
        except Exception as e:
            raise Exception(f"Error searching instances: {str(e)}")
    
    def get_instance_by_id(self, instance_id: int) -> Optional[Dict]:
        """Get single instance by ID"""
        if instance_id <= 0:
            raise ValueError("Instance ID must be positive")
        
        try:
            instance = self.dao.get_by_id(instance_id)
            if instance:
                return self._instance_to_dict(instance)
            return None
        except Exception as e:
            raise Exception(f"Error getting instance by ID: {str(e)}")
    
    def get_filter_options(self) -> Dict:
        """Get all available filter options"""
        try:
            users = self.dao.get_unique_users()
            roles = self.dao.get_unique_instance_roles()
            types = self.dao.get_unique_types()
            
            return {
                "users": sorted([self._user_to_dict(user) for user in users], key=lambda x: x['full_name']),
                "instance_roles": sorted([self._instance_role_to_dict(role) for role in roles], key=lambda x: x['name']),
                "os_types": sorted([self._type_os_to_dict(type_os) for type_os in types], key=lambda x: x['label']),
                "gpu_options": [
                    {"value": True, "label": "GPU Server"},
                    {"value": False, "label": "Non-GPU Server"}
                ]
            }
        except Exception as e:
            raise Exception(f"Error getting filter options: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """Get basic statistics"""
        try:
            total_instances = self.dao.get_total_count()
            instances = self.dao._load_data()
            
            # Initialize counters
            type_counts = {}
            gpu_count = 0
            role_counts = {}
            user_counts = {}
            
            for instance in instances:
                # Type statistics
                type_label = instance.type.label
                type_counts[type_label] = type_counts.get(type_label, 0) + 1
                
                # GPU statistics
                if instance.is_gpu_server:
                    gpu_count += 1
                
                # Role statistics
                role_name = instance.instance_role.name
                role_counts[role_name] = role_counts.get(role_name, 0) + 1
                
                # User statistics
                user_name = instance.manager.username
                user_counts[user_name] = user_counts.get(user_name, 0) + 1
            
            return {
                "total_instances": total_instances,
                "gpu_servers": gpu_count,
                "non_gpu_servers": total_instances - gpu_count,
                "gpu_percentage": round((gpu_count / total_instances) * 100, 2) if total_instances > 0 else 0,
                "by_os_type": type_counts,
                "by_role": role_counts,
                "by_user": user_counts
            }
        except Exception as e:
            raise Exception(f"Error getting statistics: {str(e)}")
    
    def validate_filters(self, **filters) -> Dict:
        """Validate filter parameters"""
        errors = []
        
        if 'user_id' in filters and filters['user_id'] is not None:
            if not isinstance(filters['user_id'], int) or filters['user_id'] <= 0:
                errors.append("user_id must be a positive integer")
        
        if 'instance_role_id' in filters and filters['instance_role_id'] is not None:
            if not isinstance(filters['instance_role_id'], int) or filters['instance_role_id'] <= 0:
                errors.append("instance_role_id must be a positive integer")
        
        if 'type_value' in filters and filters['type_value'] is not None:
            if filters['type_value'] not in [1, 2, 3]:
                errors.append("type_value must be 1 (Linux), 2 (Windows), or 3 (Unix)")
        
        if 'keyword' in filters and filters['keyword'] is not None:
            if len(filters['keyword'].strip()) == 0:
                errors.append("keyword cannot be empty")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def refresh_data(self):
        """Refresh data cache"""
        try:
            self.dao.refresh_cache()
        except Exception as e:
            raise Exception(f"Error refreshing data: {str(e)}")
    
    # Private helper methods for data conversion
    def _instance_to_dict(self, instance: Instance) -> Dict:
        """Convert Instance object to dictionary"""
        return {
            "uid": instance.uid,
            "id": instance.id,
            "name": instance.name,
            "manager": self._user_to_dict(instance.manager),
            "type": self._type_os_to_dict(instance.type),
            "os": {
                "id": instance.os.id,
                "name": instance.os.name,
                "type": instance.os.type,
                "display": instance.os.display
            },
            "is_gpu_server": instance.is_gpu_server,
            "instance_role": self._instance_role_to_dict(instance.instance_role),
            "created_at": instance.created_at.isoformat(),
            "updated_at": instance.updated_at.isoformat()
        }
    
    def _user_to_dict(self, user: User) -> Dict:
        """Convert User object to dictionary"""
        return {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}"
        }
    
    def _instance_role_to_dict(self, role: InstanceRole) -> Dict:
        """Convert InstanceRole object to dictionary"""
        return {
            "id": role.id,
            "name": role.name,
            "slug": role.slug
        }
    
    def _type_os_to_dict(self, type_os: TypeOs) -> Dict:
        """Convert TypeOs object to dictionary"""
        return {
            "value": type_os.value,
            "label": type_os.label
        }