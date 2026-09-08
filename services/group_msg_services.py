from fastapi import HTTPException
from models.group_msg import get_group_msgs,add_group_msg,delete_group_msgs
from models.group_memebers import get_member
from models.group_chat import get_group
from db.database import Session_Local
from connection_manager.group_connection import group_manager


def getmsgs(payload,groupname):
    with Session_Local() as db:
        group = get_group(db,gname=groupname)
        if group is  None:
            raise HTTPException(404,detail="Group Not Found")
        member = get_member(payload.get("user_id"),group.group_id)
        if member is None:
            raise HTTPException(401,detail=f"Not {groupname}'s member")
        return get_group_msgs(db,group.group_id)

def clearchat(groupname,payload):
    with Session_Local() as db:
        group = get_group(db,gname=groupname)
        if group is None :
            raise HTTPException(404,detail="Group Not Found")
        if group.type == "private" : 
            raise HTTPException(403,detail="Unauthorized Admin Only")
        member = get_member(payload.get("user_id"),group.group_id)
        if member is None : 
            raise HTTPException(401,detail=f"Not {groupname}'s member")
        res = delete_group_msgs(db,group.group_id)
        db.commit()
        if res is None:
            raise HTTPException(500,detail="Internal Server Error")
        return {"message" : "Chat Cleared" }

async def sendmsg(payload,groupname,data):
    with Session_Local() as db:
        group = get_group(db,gname=groupname)
        if group is None : 
            raise HTTPException(404,detail="Group Not Found")
        member = get_member(payload.get("user_id"),group.group_id)
        if member is None:
            raise HTTPException(401,detail=f"Not {groupname}'s member")
        sender,msg = payload.get("user_name"),data.msg
        msg_json = {"sender":sender,"msg" : msg}
        await group_manager.braodcast_msg(groupname,msg_json)
        add_group_msg(db,group.group_id,sender,msg)
        db.commit()
        return {"message" : "message sent successfully"}
