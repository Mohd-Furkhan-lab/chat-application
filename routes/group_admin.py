from fastapi import APIRouter,Depends
from dependencies.user_payload import get_current_user
from dependencies.admin import is_admin
from services.admin_services import getgroupmembers,addmember,updaterole,deletemember
from schemas.group_admin_schema import AddUser,UpdateRole

admin = APIRouter(prefix="/admin",tags=["admin"])

@admin.get('/{groupname}/members')
def group_members(groupname,is_admin = Depends(is_admin)):
    return getgroupmembers(groupname,is_admin)

@admin.post('/{groupname}/members')
def add_new_member(groupname,data:AddUser,is_admin = Depends(is_admin)):
    return addmember(groupname,data,is_admin)

@admin.put('/{groupname}/members/role')
def update_member_role(groupname,data:UpdateRole,is_admin = Depends(is_admin)):
    return updaterole(groupname,data,is_admin)

@admin.delete('/{groupname}/members/{username}')
def delete_member(groupname,username,is_admin = Depends(is_admin)):
    return deletemember(groupname,username,is_admin)
