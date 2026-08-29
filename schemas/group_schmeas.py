from pydantic import BaseModel

class CreateGroup(BaseModel):
    gname :  str
    type : str