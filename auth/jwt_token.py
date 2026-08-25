from fastapi import Request,HTTPException
from jwt import encode,decode,ExpiredSignatureError,InvalidTokenError
from datetime import datetime,timedelta,UTC
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

def create_access_token(user_name):
    payload = {
        "user_name" : user_name,
        "jti" : str(uuid.uuid4()),
        "type" : "access",
        "exp" : datetime.now(UTC)+timedelta(days=3)
    }
    key = os.getenv("secret_key")
    token = encode(payload,key=key,algorithm="HS256")
    return token

def create_refresh_token(user_name):
    payload = {
        "user_name" : user_name,
        "jti" : str(uuid.uuid4()),
        "type" : "refresh",
        "exp" : datetime.now(UTC)+timedelta(days=3)
    }
    key = os.getenv("secret_key")
    token = encode(payload,key=key,algorithm="HS256")
    return token

def verify_token(token):
    try :
        payload = decode(token,key=os.getenv("secret_key"),algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(401,detail="Expired Signature")
    except InvalidTokenError :
            raise HTTPException(401,detail="Invalid Token")

def new_token(token):
    payload = verify_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(401,detail="Invalid Token Type")
    new_access_token = create_access_token(payload.get("user_name"))
    return new_access_token

