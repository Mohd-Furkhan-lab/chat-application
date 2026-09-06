from fastapi import HTTPException
from db.database import Session_Local
from models.group_chat import get_group,create_group,update_no_of_members,remove_group,change_type,get_joined_groups
from models.group_memebers import add_member,calculate_no_members,get_member,delete_members
from models.users import get_user
from datetime import date

#Group Services

def get_groups(payload):
    groups = get_joined_groups(payload.get("user_id"))
    if groups is None:
        raise HTTPException(404,detail="No Joined Groups Found")
    return groups
    
def fetch_group_by_name(payload,group):
    with Session_Local() as db:
        is_group_exists = get_group(db,gname=group)
        if is_group_exists is None:
            raise HTTPException(404,detail="Group Doesnt Exists")
        member = get_member(payload.get("user_id"),is_group_exists.group_id)
        if member is None:
            raise HTTPException(401,detail= f"Not a member of {group}")
        return is_group_exists.group_name
        
def add_group(data,payload):
    user = get_user(username=payload.get("user_name"))
    with Session_Local() as db:
        is_group_exists = get_group(db,gname=data.gname)
        if is_group_exists:
            raise HTTPException(409,detail="Group Already Exists")
        try:
            group = create_group(db,data.gname,user.user_id,data.type)
            if group :
                res = add_member(db,user.user_id,group.group_id,"admin")
                if res:
                    count = calculate_no_members(db,group.group_id)
                    update_no_of_members(db,count,group.group_id)
                    db.commit()
                    return {"message" : f"{user.user_name} created {data.gname} on {date.today()}"}
        except Exception as e :
                db.rollback()
                return {"error" : f"an error occured as {e}"}

def update_group_type(data,payload):
    with Session_Local() as db:
        group = get_group(db,gname=data.gname)
        if group == None:
            raise HTTPException(404,detail="Group Not Exists")
        member = get_member(payload.get("user_id"),group.group_id)
        if member.role != "admin":
            raise HTTPException(403,detail="Forbidden")
        if data.new_type not in ["public","private"]:
            raise HTTPException(400,detail= "Invalid Type")
    res = change_type(member,data.gname,data.new_type)
    if res is None:
        raise HTTPException(500,detail= "Internal Server Error")
    return {"message" : f"Group Type Changed To {data.new_type}"}

def delete_group(group,payload):
    with Session_Local() as db:
        group = get_group(db,gname=group)
        if group == None:
            raise HTTPException(404,detail="Group Not Exists")
        member = get_member(payload.get("user_id"),group.group_id)
        if member.role != "admin":
            raise HTTPException(403,detail="Forbidden")
        try:
            res = remove_group(db,member,group)
            if res:
                delete_members(db,res.group_id)
                db.commit()
                return {"message" : "group deleted successfully"}
        except Exception as e:
            db.rollback()
            return {"message" : f"an error occured {e}"}

#Memeber Services
def join_public_group(payload,group):
    with Session_Local() as db:
        group = get_group(db,gname = group)
        if group is None:
            raise HTTPException(404,detail="Group Not Found")
        if group.type == "private" : 
            raise HTTPException(400,detail="Only admin can add members")
        is_alraedy_a_member = get_member(payload.get("user_id"),group.group_id)
        if is_alraedy_a_member:
            raise HTTPException(409,detail="already a member")
        res= add_member(db,payload.get("user_id"),group.group_id,"user")
        db.commit()
        if res is None:
            raise HTTPException(500,detail="Internal Server Error")
        return {"message" : f"joined {group} successfully!"}
    

def join_private_group(payload,data):
    if payload is None:
        raise HTTPException(401,detail="Invalid or expired token")
    with Session_Local() as db:
        group = get_group(db,gname=data.gname)
        if group is None:
            raise HTTPException(404,detail="Group Doesnt Exists")
        member = get_member(payload.get("user_id"),group.group_id)
        if member is None:
            raise HTTPException(404,detail="Not a member")
        if member.role != "admin":
            raise HTTPException(403,detail="Forbidden")
        user = get_user(username=data.user)
        if user is None:
            raise HTTPException(404,detail="User Doesnt Exists")
        is_already_member = get_member(user.user_id,group.group_id)
        if is_already_member:
            raise HTTPException(403,detail="Already A Memeber")
        res = add_member(db,user.user_id,group.group_id,"user")
        db.commit()
        if res is None:
            raise HTTPException(500,detail="Internal Server Error")
        return {"message":f"joined {group} successfully!"}


        