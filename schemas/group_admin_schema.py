from pydantic import BaseModel

class AddUser(BaseModel):
    username : str
    role : str
