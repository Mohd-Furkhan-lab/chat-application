from fastapi import HTTPException
from db.database import Session_Local
from models.group_chat import get_group,create_group
from auth.jwt_token import verify_token
from models.users import get_user
from models.group_memebers import add_member

from datetime import date

def add_group(data,token):
    paylod = verify_token(token)
    if paylod is None:
        raise HTTPException(401,detail="Unauthorized")
    user = get_user(username=paylod.get("user_name"))
    is_group_exists = get_group(data.gname)
    if is_group_exists:
        raise HTTPException(409,detail="Group Already Exists")
    with Session_Local() as db:
        try:
            group = create_group(db,data.gname,user.user_id,data.type)
            if group :
                res = add_member(db,user.user_id,group.group_id,"admin")
                if res:
                    db.commit()
                    return {"message" : f"{user.user_name} created {data.gname} on {date.today()}"}
        except Exception as e :
            db.rollback()
            return {"error" : f"an error occured as {e}"}
            