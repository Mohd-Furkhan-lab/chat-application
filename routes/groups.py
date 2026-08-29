from fastapi import APIRouter,Request
from schemas.group_schmeas import CreateGroup
from services.group_services import add_group,delete_group

groups = APIRouter(prefix="/groups",tags = ["groups"])

@groups.post('/')
def newgroup(data:CreateGroup,request:Request):
    token = request.cookies.get("access")
    return add_group(data,token)

@groups.delete('/{group_id}')
def deletegroup(group_id,request:Request):
    token = request.cookies.get("access")
    return delete_group(group_id,token)

