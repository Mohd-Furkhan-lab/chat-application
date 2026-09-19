from fastapi import Depends,HTTPException
from config.database  import Session_Local
from .user_payload import get_current_user
from models.group_chat import get_group
from models.group_memebers import get_member

def is_admin(groupname : str , payload = Depends(get_current_user)):
    with Session_Local() as db:
        group = get_group(db,gname=groupname)
        member = get_member(payload.get("user_id"),group.group_id)
        if member is None:
            raise HTTPException(401,detail="Not a group member")
        if member.role != "admin":
            raise HTTPException(401,detail="Unauthorized Admin Only")
        return member