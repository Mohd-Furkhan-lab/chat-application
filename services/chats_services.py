from fastapi import HTTPException
from models.conversation import get_chats,get_convo,clear_convo
from models.messages import get_msg
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
    if chats:
        return {"chats" : chats}
    else: 
        raise HTTPException(404,detail="No Chats Found")

def get_chat(token,user_name):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Token Missing")
    jti = payload.get("jti")
    is_expired(jti) 
    user = payload.get("user_name")
    convo = get_convo(user,user_name)
    if convo:
        convo_id = convo.convo_id
        chat = get_msg(convo_id)
        if chat:
            return chat
        else:
            return {"message" : "no chat found"}
    else:
        return {"message" : f"no contact named {user_name}"}


def delete_convo(token,user_name):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Token Missing")
    jti = payload.get("jti")
    is_expired(jti) 
    user = payload.get("user_name")
    convo = get_convo(user,user_name)
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
        