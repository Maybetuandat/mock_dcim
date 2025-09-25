# instance_dao.py
import json
from typing import List, Optional
from datetime import datetime
from model import User, Os, InstanceRole, TypeOs, Instance


class InstanceDAO:
    def __init__(self, json_file_path: str = "data.json"):
        self.json_file_path = json_file_path
        self._instances: List[Instance] = []
        self._load_data()
    
    def _load_data(self):
     
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            self._instances = []
            for item in data:
                # Parse datetime strings
                created_at = datetime.fromisoformat(item['created_at'].replace('+07:00', '+07:00'))
                updated_at = datetime.fromisoformat(item['updated_at'].replace('+07:00', '+07:00'))
                
                # Create nested objects
                user = User(**item['manager'])
                type_os = TypeOs(**item['type'])
                os = Os(**item['os'])
                instance_role = InstanceRole(**item['instance_role'])
                
                # Create Instance object
                instance = Instance(
                    uid=item['uid'],
                    id=item['id'],
                    name=item['name'],
                    manager=user,
                    type=type_os,
                    os=os,
                    is_gpu_server=item['is_gpu_server'],
                    instance_role=instance_role,
                    created_at=created_at,
                    updated_at=updated_at
                )
                self._instances.append(instance)
                
        except FileNotFoundError:
            print(f"File {self.json_file_path} not found")
            self._instances = []
        except json.JSONDecodeError:
            print(f"Invalid JSON in file {self.json_file_path}")
            self._instances = []
    
    def get_all(self) -> List[Instance]:
        """Get all instances"""
        return self._instances.copy()
    
    def get_by_id(self, instance_id: int) -> Optional[Instance]:
        """Get instance by ID"""
        for instance in self._instances:
            if instance.id == instance_id:
                return instance
        return None
    
    def filter_by_user(self, user_id: int) -> List[Instance]:
        """Filter instances by user ID"""
        return [instance for instance in self._instances if instance.manager.id == user_id]
    
    def filter_by_instance_role(self, role_id: int) -> List[Instance]:
        """Filter instances by instance role ID"""
        return [instance for instance in self._instances if instance.instance_role.id == role_id]
    
    def filter_by_name(self, name: str) -> List[Instance]:
        """Filter instances by name (IP address) - case insensitive partial match"""
        name_lower = name.lower()
        return [instance for instance in self._instances if name_lower in instance.name.lower()]
    
    def count(self) -> int:
        """Get total count of instances"""
        return len(self._instances)