from pydantic import BaseModel

class AddUser(BaseModel):
    username : str
    role : str

class UpdateRole(BaseModel):
    username : str
    new_role : str