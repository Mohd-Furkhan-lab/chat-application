from sqlalchemy import Column,String,Integer
from config.database  import BaseModel,Session_Local

class User(BaseModel):
    __tablename__ = "users"
    user_id = Column(Integer,autoincrement=True,primary_key=True)
    user_name = Column(String,unique=True)
    email =  Column(String,nullable=False)
    password =  Column(String,nullable=False)
    profile_pic = Column(String,nullable=False,default="")

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

def add_pic(userid,img_url):
    with Session_Local() as db:
        user=db.query(User).filter(User.user_id==userid).first()
        user.profile_pic=img_url
        db.commit()
        return user
