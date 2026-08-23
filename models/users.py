from sqlalchemy import Column,String,Integer
from db.database import BaseModel,Session_Local

class User(BaseModel):
    __tablename__ = "users"
    user_id = Column(Integer,autoincrement=True,primary_key=True)
    user_name = Column(String,unique=True)
    email =  Column(String,nullable=False)
    password =  Column(String,nullable=False)

def add_user(username,email,password):
    with Session_Local() as db:
        user = User(
            user_name = username,
            email = email,
            password = password
        )
        db.add(user)
        db.commit()
        return True

def get_user(email=None,username = None):
    with Session_Local() as db:
        if email :
            user = db.query(User).filter(User.email == email).first()
            return user
        if username :
            user = db.query(User).filter(User.user_name == username).first()
            return user