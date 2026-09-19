from models.group_chat import get_group
from models.group_memebers import get_member,get_members,add_member,update_user_role,remove_group_member
from models.users import get_user
from models.group_msg import delete_group_msgs
from config.database  import Session_Local
from fastapi import HTTPException

def getgroupmembers(groupname,is_admin):
    if is_admin :
        with Session_Local() as db:
            group = get_group(db,gname=groupname)
            if group is None:
                raise HTTPException(404,detail="Group Not Found")
            memebers = get_members(group.group_id)
            if memebers is None:
                return {"message" : "No memebrs"}
            return {"message" : {"members" : [[m[0],m[1]] for m in memebers]}}

def addmember(groupname,data,is_admin):
    if is_admin:
        with Session_Local() as db:
            group = get_group(db,gname=groupname)
            alraedyamember = get_member(get_user(username=data.username).user_id,group.group_id)
            if alraedyamember:
                raise HTTPException(409,detail="Already a member")
            res = add_member(db,get_user(username=data.username).user_id,group.group_id,data.role)
            db.commit()
            if res is None:
                raise HTTPException(500,detail="Internal Server Error")
            return {"message" : f"{data.username} added to {groupname} successfully ! "}
    

def updaterole(groupname,data,is_admin):
    if is_admin:
        with Session_Local() as db:
            group = get_group(db,gname=groupname)
            if group is None:
                raise HTTPException(404,detail="Group Not Found")
            member = get_member(get_user(username=data.username).user_id,group.group_id)
            if member is None:
                raise HTTPException(404,detail="Not group member")
            res = update_user_role(db,member.user_id,group.group_id,data.new_role)
            db.commit()
            if res is None:
                raise HTTPException(500,detail="Internal Server Error")
            return {"messsage" : f"{data.username} udpated to {data.new_role}"}

def deletemember(groupname,username,is_admin):
    if is_admin:
        with Session_Local() as db:
            group = get_group(db,gname=groupname)
            if group is None:
                raise HTTPException(404,detail="Group Not Found")
            member = get_member(get_user(username=username).user_id,group.group_id)
            if member is None:
                raise HTTPException(404,detail="Not group member")
            res = remove_group_member(group.group_id,member.user_id)
            if res is None:
                raise HTTPException(500,detail="Internal Server Error")
            return {"message" : f"{username} deleted successfully"}

def clearchat(groupname,is_admin):
    if is_admin:
        with Session_Local() as db:
            group = get_group(db,gname=groupname)
            if group is None :
                raise HTTPException(404,detail="Group Not Found")
            res = delete_group_msgs(db,group.group_id)
            db.commit()
            if res is None:
                raise HTTPException(500,detail="Internal Server Error")
            return {"message" : "Chat Cleared" }