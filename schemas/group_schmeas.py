from pydantic import BaseModel

class CreateGroup(BaseModel):
    gname :  str
    type : str

class  Updatetype(BaseModel):
    gname :  str
    new_type : str