from fastapi import APIRouter,Depends
from dependencies.user_payload import get_current_user
from services.admin_services import getgroupmembers,addmember
from schemas.group_admin_schema import AddUser

admin = APIRouter(prefix="/admin",tags=["admin"])

@admin.get('/{groupname}/members')
def group_members(groupname,payload = Depends(get_current_user)):
    return getgroupmembers(groupname,payload)

@admin.post('/{groupname}/members')
def add_new_member(groupname,data:AddUser,payload = Depends(get_current_user)):
    return addmember(groupname,data,payload)

@admin.put('/{groupname}/members/{username}')
def update_member_role(groupname,username):
    return {"message" : f"{username} role udpated"}

@admin.delete('/{groupname}/members/{username}')
def delete_member(groupname,username):
    return {"message" : f"{username} removed"}
