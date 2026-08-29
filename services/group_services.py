from fastapi import HTTPException
from db.database import Session_Local
from models.group_chat import get_group,create_group,update_no_of_members
from models.group_memebers import add_member,calculate_no_members
from models.users import get_user
from auth.jwt_token import verify_token
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
                    count = calculate_no_members(db,group.group_id)
                    update_no_of_members(db,count,group.group_id)
                    db.commit()
                    return {"message" : f"{user.user_name} created {data.gname} on {date.today()}"}
        except Exception as e :
            db.rollback()
            return {"error" : f"an error occured as {e}"}
            