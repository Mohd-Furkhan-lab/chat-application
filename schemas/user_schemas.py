from pydantic import BaseModel,EmailStr,ConfigDict

class UserAuth(BaseModel):
    email  : EmailStr
    password : str

class Msg(BaseModel):
    to : str
    msg : str

class Info(BaseModel):
    user_name : str
    email : str

    model_config = ConfigDict(from_attributes=True)