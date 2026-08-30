from fastapi import APIRouter,Request
from schemas.group_schmeas import CreateGroup,Updatetype
from services.group_services import add_group,delete_group,update_group_type,get_groups,fetch_group_by_name

groups = APIRouter(prefix="/groups",tags = ["groups"])


@groups.get('/')
def get_all_groups(request:Request):
    token = request.cookies.get("access")
    return get_groups(token)

@groups.get('/{group_name}')
def get_group(request:Request,group_name):
    token = request.cookies.get("access")
    return fetch_group_by_name(token,group_name)

@groups.post('/')
def newgroup(data:CreateGroup,request:Request):
    token = request.cookies.get("access")
    return add_group(data,token)

@groups.delete('/{group_name}')
def deletegroup(group_name,request:Request):
    token = request.cookies.get("access")
    return delete_group(group_name,token)

@groups.put('/')
def updatetype(data:Updatetype,request:Request):
    token = request.cookies.get("access")
    return update_group_type(data,token)