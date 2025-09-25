from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from instance_dao import InstanceDAO
from instance_service import InstanceService
from model import Instance


dao = InstanceDAO("data.json")
service = InstanceService(dao)


router = APIRouter(prefix="/api/v1/instances", tags=["instances"])


@router.get("/", response_model=Dict[str, Any])
async def get_instances(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    username: Optional[str] = Query(None, description="Filter by username"),
    instance_role_name: Optional[int] = Query(None, description="Filter by instance role instance name"),
    name: Optional[str] = Query(None, description="Filter by instance name (IP address)")
) -> Dict[str, Any]:
    """
    Get instances with pagination and filtering
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)
    - **user_id**: Filter instances by manager user ID
    - **role_id**: Filter instances by role ID (1=Web Server, 2=Database Server, 3=Compute Server, 4=File Server)
    - **name**: Filter instances by name/IP address (partial match, case insensitive)
    """
    try:
        result = service.get_instances(
            page=page,
            page_size=page_size,
            username=username,
            instance_role_name=instance_role_name,
            name=name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{instance_id}", response_model=Instance)
async def get_instance(instance_id: int) -> Instance:
   
    instance = service.get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_statistics() -> Dict[str, Any]:
  
    try:
        return service.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")