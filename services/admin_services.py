from models.group_chat import get_group
from models.group_memebers import get_member,get_members,add_member
from models.users import get_user
from db.database import Session_Local
from fastapi import HTTPException

def getgroupmembers(groupname,paylaod):
    with Session_Local() as db:
        group = get_group(db,gname=groupname)
        if group is None:
            raise HTTPException(404,detail="Group Not Found")
        admin = get_member(paylaod.get("user_id"),group.group_id)
        if admin is None:
            raise HTTPException(403,detail="Not a member")
        if admin.role != "admin" :
            raise HTTPException(403,detail="Forbidden")
        memebers = get_members(group.group_id)
        if memebers is None:
            return {"message" : "No memebrs"}
        return {"message" : {"members" : [[m[0],m[1]] for m in memebers]}}

def addmember(groupname,data,payload):
    if payload is None:
        raise HTTPException(401,detail="Invalid or expired token")
    with Session_Local() as db:
        group = get_group(db,gname=groupname)
        if group is None : 
            raise HTTPException(404,detail="No Group Found")
        admin = get_member(payload.get("user_id"),group.group_id)
        if admin is None:
            raise HTTPException(403,detail=f"Not a member of {groupname}")
        if admin.role != "admin" : 
            raise HTTPException(401,detail="Unauthorized Admin only")
        alraedyamember = get_member(get_user(username=data.username).user_id,group.group_id)
        if alraedyamember:
            raise HTTPException(409,detail="Already a member")
        res = add_member(db,get_user(username=data.username).user_id,group.group_id,data.role)
        db.commit()
        if res is None:
            raise HTTPException(500,detail="Internal Server Error")
        return {"message" : f"{data.username} added to {groupname} successfully ! "}
    
        


