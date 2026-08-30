from models.users import add_user,get_user
from fastapi import HTTPException
from utlis.username_generator import random_username
from auth.jwt_token import create_access_token,create_refresh_token,verify_token,new_token
from connection_manager.manage_connection import manager
from models.conversation import get_convo,add_new_convo
from models.messages import add_msg
from models.token_blacklist import revoketoken,is_revoked
import bcrypt
import redis
import time
import os

r = redis.from_url(os.getenv("redis_url"))

def new_user(data):
    email,password = data.email,data.password
    is_auser = get_user(email)
    if is_auser:
        raise HTTPException(409,detail="User Already Exists")
    user_name = random_username()
    hash = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode("utf-8")
    res = add_user(user_name,email,hash)
    if not res:
        raise HTTPException(500,detail="Internal Server Error")
    return {"message" : "signed up successfully",  "user_name": user_name}

def user_login(data):
    email,password = data.email,data.password
    is_auser = get_user(email)
    if is_auser is None:
        raise HTTPException(404,detail="User Not Found")
    hash_password = is_auser.password
    is_valid = bcrypt.checkpw(password.encode('utf-8'),hash_password.encode('utf-8'))
    if is_valid is False:
        raise HTTPException(401,detail="Invalid Credentials")
    access_token = create_access_token(is_auser.user_name,is_auser.user_id)
    refresh_token = create_refresh_token(is_auser.user_name,is_auser.user_id)
    return access_token,refresh_token

def user_info(token):
    payload = verify_token(token)
    if not payload :
        raise HTTPException(401,detail="Unauthorized")
    jti = payload.get("jti")
    is_expired(jti)    
    user_name = payload.get("user_name")
    info = get_user(username=user_name)
    if info is None:
        raise HTTPException(404,detail="User Not Found")
    return info


async def sendmsg(data,token):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401,detail="Unauthorized")
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


def refresh(token):
    paylaod = verify_token(token)
    if not paylaod:
        raise HTTPException(401,detail="Unauthorized")
    jti = paylaod.get("jti")
    is_blacklisted = is_revoked(jti)
    if is_blacklisted:
        raise HTTPException(401,detail="Token Revoked")
    newtoken = new_token(token)
    if newtoken :
        return newtoken
    else:
        raise HTTPException(500,detail="Internal Server Error") 


async def logout(access_token,refresh_toke):
        access_paylaod = verify_token(access_token)
        refersh_paylaod = verify_token(refresh_toke)
        if access_paylaod is None:
            raise HTTPException(401,detail="Unauthorized")
        if refersh_paylaod is None:
            raise HTTPException(401,detail="Unauthorized")
        if refersh_paylaod.get("type") != "refresh":
            raise HTTPException(401,detail="Invalid Token Type")
        jti = access_paylaod.get("jti")
        remaining_time = access_paylaod.get("exp") - int(time.time())
        r.set(f"blacklist:{jti}",1,remaining_time)
        jti = refersh_paylaod.get("jti")
        exp = refersh_paylaod.get("exp")
        user_name = refersh_paylaod.get("user_name")
        res = revoketoken(jti,exp,True)
        if res is None:
            raise HTTPException(500,detail="Internal Server Error")
        ws = manager.active_connection.get(user_name)
        if ws:
            await ws.close()
            manager.remove_connection(user_name)
        return {"message" : "logout successfully"}

def is_expired(jti):
    is_exists = r.get(f"blacklist:{jti}")
    if is_exists:
        raise HTTPException(401,detail="Revoked Token")
    
