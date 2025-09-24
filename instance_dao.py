# dao/instance_dao.py
import json
from typing import List, Optional, Tuple
from datetime import datetime

import User
from instance import Instance
from os import Os
from instance_role import InstanceRole
from typeos import TypeOs



class InstanceDAO:
    def __init__(self, json_file_path: str = "data.json"):
        self.json_file_path = json_file_path
        self._instances_cache = None
    
    def _load_data(self) -> List[Instance]:
        """Load data from JSON file and convert to Instance objects"""
        if self._instances_cache is None:
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                instances = []
                for item in data:
                    # Convert datetime strings to datetime objects
                    created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                    updated_at = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                    
                    # Create nested objects
                    manager = User(**item['manager'])
                    type_os = TypeOs(**item['type'])
                    os_obj = Os(**item['os'])
                    instance_role = InstanceRole(**item['instance_role'])
                    
                    # Create Instance object
                    instance = Instance(
                        uid=item['uid'],
                        id=item['id'],
                        name=item['name'],
                        manager=manager,
                        type=type_os,
                        os=os_obj,
                        is_gpu_server=item['is_gpu_server'],
                        instance_role=instance_role,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    instances.append(instance)
                
                self._instances_cache = instances
                return self._instances_cache
                
            except FileNotFoundError:
                raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format in file: {self.json_file_path}")
            except Exception as e:
                raise Exception(f"Error loading data: {str(e)}")
        
        return self._instances_cache
    
    def get_instances(self, skip: int = 0, limit: int = 10) -> List[Instance]:
        """Get instances with pagination"""
        instances = self._load_data()
        return instances[skip:skip + limit]
    
    def get_by_id(self, instance_id: int) -> Optional[Instance]:
        """Get instance by ID"""
        instances = self._load_data()
        for instance in instances:
            if instance.id == instance_id:
                return instance
        return None
    
    def search_instances(
        self,
        keyword: Optional[str] = None,
        user_id: Optional[int] = None,
        instance_role_id: Optional[int] = None,
        type_value: Optional[int] = None,
        is_gpu_server: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Instance], int]:
        """Search instances with filters and pagination"""
        instances = self._load_data()
        filtered_instances = []
        
        for instance in instances:
            # Apply filters
            if keyword and keyword.strip():
                keyword_lower = keyword.strip().lower()
                if (keyword_lower not in instance.name.lower() and 
                    keyword_lower not in instance.manager.username.lower() and
                    keyword_lower not in f"{instance.manager.first_name} {instance.manager.last_name}".lower()):
                    continue
            
            if user_id is not None and instance.manager.id != user_id:
                continue
            
            if instance_role_id is not None and instance.instance_role.id != instance_role_id:
                continue
            
            if type_value is not None and instance.type.value != type_value:
                continue
            
            if is_gpu_server is not None and instance.is_gpu_server != is_gpu_server:
                continue
            
            filtered_instances.append(instance)
        
        total = len(filtered_instances)
        paginated_instances = filtered_instances[skip:skip + limit]
        
        return paginated_instances, total
    
    def get_total_count(self) -> int:
        """Get total number of instances"""
        instances = self._load_data()
        return len(instances)
    
    def get_unique_users(self) -> List[User]:
        """Get list of unique users (managers)"""
        instances = self._load_data()
        users_dict = {}
        
        for instance in instances:
            user_id = instance.manager.id
            if user_id not in users_dict:
                users_dict[user_id] = instance.manager
        
        return list(users_dict.values())
    
    def get_unique_instance_roles(self) -> List[InstanceRole]:
        """Get list of unique instance roles"""
        instances = self._load_data()
        roles_dict = {}
        
        for instance in instances:
            role_id = instance.instance_role.id
            if role_id not in roles_dict:
                roles_dict[role_id] = instance.instance_role
        
        return list(roles_dict.values())
    
    def get_unique_types(self) -> List[TypeOs]:
        """Get list of unique OS types"""
        instances = self._load_data()
        types_dict = {}
        
        for instance in instances:
            type_value = instance.type.value
            if type_value not in types_dict:
                types_dict[type_value] = instance.type
        
        return list(types_dict.values())
    
    def refresh_cache(self):
        """Refresh the internal cache (useful if JSON file is updated)"""
        self._instances_cache = None