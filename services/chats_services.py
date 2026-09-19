from fastapi import HTTPException
from models.conversation import get_chats,get_convo,clear_convo,add_new_convo,Conversation
from models.messages import get_msg
from models.users import get_user
from services.user_services import is_expired
from db.database import Session_Local
from models.messages import add_msg
from models.users import User
from connection_manager.user_connection import manager

def getallchats(payload):
    user = payload.get("user_name")
    jti = payload.get("jti")
    is_expired(jti) 
    chats = get_chats(user)
    if chats:
        return {"chats" : chats}
    else: 
        raise HTTPException(404,detail="No Chats Found")

def get_chat(payload,user2):
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


def add_user(payload,user2):
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

async def sendmsg(data,payload):
    jti = payload.get("jti")
    is_expired(jti)
    sender = payload.get("user_name")
    to,msg = data.to,data.msg
    msg_json = {"from":sender,"message" : msg}
    user_1,user_2 = sorted([sender,to])
    convo = get_convo(user_1,user_2)
    if convo is None:
        raise HTTPException(404,detail="Chat not found")
    add_msg(convo.convo_id,sender,msg)
    is_online = manager.active_connection.get(to)
    if is_online:
        await manager.braodcast_msg(msg_json,to)
        return {"message" : "sent successfully"}
    else:
        return {"message" : "user offline"}

def delete_convo(payload,user2):
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