from fastapi import APIRouter,Request,Depends
from dependencies.user_payload import get_current_user
from schemas.group_schmeas import CreateGroup,Updatetype
from services.group_services import add_group,delete_group,update_group_type,get_groups,fetch_group_by_name,join_public_group

groups = APIRouter(prefix="/groups",tags = ["groups"])


@groups.get('/')
def get_all_groups(payload = Depends(get_current_user)):
    return get_groups(payload)

@groups.get('/{group_name}')
def get_group(group_name,payload = Depends(get_current_user)):
    return fetch_group_by_name(payload,group_name)

@groups.post('/')
def newgroup(data:CreateGroup,payload = Depends(get_current_user)):
    return add_group(data,payload)

@groups.delete('/{group_name}')
def deletegroup(group_name,payload = Depends(get_current_user)):
    return delete_group(group_name,payload)

@groups.put('/')
def updatetype(data:Updatetype,payload = Depends(get_current_user)):
    return update_group_type(data,payload)


#Members
@groups.post('/members/{group_name}')
def join_group(group_name,payload = Depends(get_current_user)):
    return join_public_group(payload,group_name)


