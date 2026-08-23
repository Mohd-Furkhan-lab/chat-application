from fastapi import APIRouter,Response,Request,HTTPException
from schemas.user_schemas import UserAuth,Msg,Info
from services.user_services import new_user,user_login,user_info,refresh,logout


users = APIRouter(prefix = "/users",tags = ["users"])


@users.get('/me',response_model=Info)
def get_user_info(request : Request):
    access_token = request.cookies.get("access")
    data = user_info(access_token)

    return data

@users.post('/signup')
def signup(data : UserAuth):
    return new_user(data) 

@users.post('/login')
def login(response:Response,data : UserAuth):
    access_token,refresh_token =  user_login(data)
    response.set_cookie(
        key="access",
        value=access_token,
        httponly=True,
        secure=False
    )
    response.set_cookie(
            key="refresh",
            value=refresh_token,
            httponly=True,
            secure=False
        )
    return {"message" : "logedin successfully"}

@users.post('/logout')
async def user_logout(request:Request,response:Response):
    a_token = request.cookies.get("access")
    r_token = request.cookies.get("refresh")
    res = await logout(a_token,r_token)
    response.delete_cookie(key="access")
    response.delete_cookie(key="refresh")
    return res

@users.post('/refresh')
def new_access_token(request:Request,response:Response):
    token = request.cookies.get("refresh")
    new_token = refresh(token)
    response.set_cookie(
        key = "access",
        value = new_token,
        secure = False,
        httponly = True

    )
    return {"message" : "new token generated"}