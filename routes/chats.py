from fastapi import APIRouter,Request,HTTPException,Depends
from services.chats_services import getallchats,get_chat,delete_convo,add_user,sendmsg
from schemas.user_schemas import Msg
from dependencies.user_payload import get_current_user

chats = APIRouter(prefix="/chat",tags=["chats"])

@chats.get('/contacts')
def get_all_chats(payload = Depends(get_current_user)):
    return getallchats(payload)

@chats.post('/send-msg')
async def send_msg(data:Msg,payload = Depends(get_current_user)):
    res = await sendmsg(data,payload)
    return res

@chats.get('/{username}')
def getchat(username,payload = Depends(get_current_user)):
    return get_chat(payload,username)

@chats.post('/{username}')
def adduser(username,payload = Depends(get_current_user)):
    return add_user(payload,username)


@chats.delete('/clear-chat/{username}')
def clear_chat(username,payload = Depends(get_current_user)):
    return delete_convo(payload,username)