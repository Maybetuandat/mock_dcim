from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from instance_dao import InstanceDAO
from instance_service import InstanceService
from model import Instance, InstanceRole


dao = InstanceDAO("data.json")
service = InstanceService(dao)


router = APIRouter(prefix="/api/v1/instances", tags=["instances"])


@router.get("/", response_model=Dict[str, Any])
async def get_instances(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user_id: Optional[str] = Query(None, description="Filter by username"),
    instance_role_id: Optional[int] = Query(None, description="Filter by instance role ID"),
    name: Optional[str] = Query(None, description="Filter by instance name (IP address)")
) -> Dict[str, Any]:
   
    try:
        result = service.get_instances(
            page=page,
            page_size=page_size,
            user_id=user_id,
            instance_role_id=instance_role_id,
            name=name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
@router.get("/instance_roles", response_model=List[InstanceRole])
async def get_instance_roles():
    roles = service.get_instance_roles()
    return roles

