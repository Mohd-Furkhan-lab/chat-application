from fastapi import Depends,Request,HTTPException
from auth.jwt_token import verify_token

def get_current_user(request:Request):
    token = request.cookies.get("access")
    if token is None:
        raise HTTPException(401,detail="Authorization token missing")
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(401,detail="Invalid or expired token")
    return payload