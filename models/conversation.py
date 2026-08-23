from sqlalchemy import Column,String,Integer
from db.database import BaseModel,Session_Local

class Conversation(BaseModel):
    __tablename__ = "convo"
    convo_id = Column(Integer,primary_key=True,autoincrement=True)
    sender = Column(String,nullable=False)
    reciever = Column(String,nullable=False)

def get_convo(sender,reciever):
    with Session_Local() as db:
        id = db.query(Conversation).filter(Conversation.sender == sender,Conversation.reciever == reciever).first()
        if id:
            return id

def get_chats(user):
    with Session_Local() as db:
        sent_chats = db.query(Conversation.reciever).filter(Conversation.sender == user).all()
        received_chats = db.query(Conversation.sender).filter(Conversation.reciever == user).all()
        all_chats = set([chat[0] for chat in sent_chats] + [chat[0] for chat in received_chats])
        return list(all_chats)


def add_new_convo(sender,reciever):
    with Session_Local() as db:
        convo = Conversation(
            sender = sender,
            reciever = reciever
        )
        db.add(convo)
        db.commit()

def clear_convo(convo_id,db):
    convo = db.query(Conversation).filter(Conversation.convo_id == convo_id).first()
    if convo:
        db.delete(convo)