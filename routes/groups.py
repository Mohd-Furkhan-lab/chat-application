from fastapi import APIRouter,Request,Depends
from dependencies.user_payload import get_current_user
from schemas.group_schmeas import CreateGroup,Updatetype,SendMsg
from services.group_services import add_group,delete_group,update_group_type,get_groups,fetch_group_by_name,join_public_group
from services.group_msg_services import getmsgs,sendmsg,clearchat

groups = APIRouter(prefix="/groups",tags = ["groups"])


@groups.get('/')
def get_all_groups(payload = Depends(get_current_user)):
    return get_groups(payload)

@groups.get('/{groupname}')
def get_group(groupname,payload = Depends(get_current_user)):
    return fetch_group_by_name(payload,groupname)

@groups.get('/{groupname}/chat')
def get_groupchat(groupname,payload = Depends(get_all_groups)):
    return getmsgs(payload,groupname)

@groups.post('/')
def newgroup(data:CreateGroup,payload = Depends(get_current_user)):
    return add_group(data,payload)

@groups.post('/members/{groupname}')
def join_group(groupname,payload = Depends(get_current_user)):
    return join_public_group(payload,groupname)

@groups.put('/')
def updatetype(data:Updatetype,payload = Depends(get_current_user)):
    return update_group_type(data,payload)

@groups.delete('/{groupname}')
def deletegroup(groupname,payload = Depends(get_current_user)):
    return delete_group(groupname,payload)

@groups.post('/{groupname}/chat')
async def send_group_msg(groupname,data:SendMsg,payload = Depends(get_current_user)):
    return await sendmsg(payload,groupname,data)
