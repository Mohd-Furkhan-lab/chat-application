from fastapi import APIRouter,Request
from schemas.group_schmeas import CreateGroup
from services.group_services import add_group

groups = APIRouter(prefix="/groups",tags = ["groups"])

@groups.post('/')
def new_group(data:CreateGroup,request:Request):
    token = request.cookies.get("access")
    return add_group(data,token)