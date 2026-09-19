from sqlalchemy import Column,String,Integer
from config.database  import BaseModel,Session_Local
from sqlalchemy import or_, and_
from models.users import User

class Conversation(BaseModel):
    __tablename__ = "convo"
    convo_id = Column(Integer,primary_key=True,autoincrement=True)
    user1 = Column(String,nullable=False)
    user2 = Column(String,nullable=False)

def get_convo(user1,user2):
    with Session_Local() as db:
        id = db.query(Conversation).filter(Conversation.user1 == user1,Conversation.user2 == user2).first()
        if id:
            return id


def get_chats(user):
    with Session_Local() as db:
        chats = (
            db.query(Conversation, User.user_name, User.profile_pic)
            .join(User,or_(and_(Conversation.user1 == user,User.user_name == Conversation.user2),and_(Conversation.user2 == user,User.user_name == Conversation.user1)))
            .filter(or_(Conversation.user1 == user,Conversation.user2 == user)).all())
        return [
            {
                "username": username,
                "pfp": pfp
            }
            for chat, username, pfp in chats
        ]


def add_new_convo(user1,user2):
    with Session_Local() as db:
        convo = Conversation(
            user1 = user1,
            user2 = user2
        )
        db.add(convo)
        db.commit()
        return True

def clear_convo(convo_id,db):
    convo = db.query(Conversation).filter(Conversation.convo_id == convo_id).first()
    if convo:
        db.delete(convo)