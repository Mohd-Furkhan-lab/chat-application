from fastapi import HTTPException
from models.conversation import get_chats,get_convo,clear_convo,add_new_convo
from models.messages import get_msg
from models.users import get_user
from auth.jwt_token import verify_token
from services.user_services import is_expired
from db.database import Session_Local


def getallchats(token):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Token Missing")
    user = payload.get("user_name")
    jti = payload.get("jti")
    is_expired(jti) 
    chats = get_chats(user)
    print(chats)
    if chats:
        return {"chats" : chats}
    else: 
        raise HTTPException(404,detail="No Chats Found")

def add_user(token,user2):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Token Missing")
    user = payload.get("user_name")
    jti = payload.get("jti")
    is_expired(jti)
    is_user_exists = get_user(username=user2)
    if is_user_exists is None:
        raise HTTPException(404,detail="User Not Found")
    user_1,user_2 = sorted([user,user2])
    is_convo_exists = get_convo(user_1,user_2)
    if is_convo_exists:
        raise HTTPException(409,detail="Chat Already Exists")
    res = add_new_convo(user_1,user_2)
    if res is None:
        raise HTTPException(500,detail="Internal Server Error")
    return {"message" : f"connected with {user2}"}


def get_chat(token,user2):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Token Missing")
    jti = payload.get("jti")
    is_expired(jti) 
    user = payload.get("user_name")
    user_1,user_2 = sorted([user,user2])
    convo = get_convo(user_1,user_2)
    if convo:
        convo_id = convo.convo_id
        chat = get_msg(convo_id)
        if chat:
            return {"current_user":user,"messages":chat}
        else:
            return {"message" : "no chat found"}
    else:
        return {"message" : f"no contact named {user2}"}


def delete_convo(token,user2):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Token Missing")
    jti = payload.get("jti")
    is_expired(jti) 
    user = payload.get("user_name")
    user_1,user_2 = sorted([user,user2])
    convo = get_convo(user_1,user_2)
    if convo is None:
        raise HTTPException(404,detail="Contact not found")
    with Session_Local() as db:
        try :
            clear_convo(convo.convo_id,db)
            db.commit()
            return {"message" : "chat cleared successfully"}
        except Exception as e:
            db.rollback()
            return {"message" : f"an error occured as {e}"}
        