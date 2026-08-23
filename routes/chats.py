from fastapi import APIRouter,Request,HTTPException
from services.chats_services import getallchats,get_chat,delete_convo
from services.user_services import sendmsg
from schemas.user_schemas import Msg

chats = APIRouter(prefix="/chat",tags=["chats"])

@chats.get('/contacts')
def get_all_chats(request:Request):
    token = request.cookies.get("access")
    return getallchats(token)

@chats.get('/{username}')
def getchat(request:Request,username):
    token = request.cookies.get("access")
    return get_chat(token,username)

@chats.post('/send-msg')
async def send_msg(data:Msg,request:Request):
    token = request.cookies.get("access")
    if token is None:
        raise HTTPException(401,detail="Unauthorized")
    res = await sendmsg(data,token)
    return res

@chats.delete('/clear-chat/{username}')
def clear_chat(request:Request,username):
    token = request.cookies.get("access")
    return delete_convo(token,username)