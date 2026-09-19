from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,Enum
from config.database  import BaseModel,Session_Local
from utlis.media_types import MediaType
from datetime import datetime,UTC

class Messages(BaseModel):
    __tablename__ = "msg"
    msg_id = Column(Integer,primary_key=True,autoincrement=True)
    convo_id = Column(Integer,ForeignKey("convo.convo_id",ondelete="CASCADE"))
    msg = Column(String,nullable=True)
    sender = Column(String,nullable=False)
    media_url = Column(String,nullable=True)
    media_type = Column(Enum(MediaType),nullable=True)
    timestamp = Column(DateTime,default=lambda: datetime.now(UTC))


def get_msg(convo_id):
    with Session_Local() as db:
        msgs = db.query(Messages.timestamp,Messages.msg,Messages.sender,Messages.media_url,Messages.media_type).filter(Messages.convo_id == convo_id).all()
        return [
            {
                "msg": message.msg,
                "sender": message.sender,
                "timestamp": message.timestamp,
                "media" : message.media_url,
                "type" : message.media_type
            }
            for message in msgs
        ]

def add_msg(convo_id,sender,msg):
    with Session_Local() as db:
        msg = Messages(
            convo_id = convo_id,
            sender = sender,
            msg = msg
        )
        db.add(msg)
        db.commit()


def add_media(convo_id,sender,url,type):
    with Session_Local() as db:
        media = Messages(
            convo_id = convo_id,
            sender = sender,
            media_url = url,
            media_type = type
        )
        db.add(media)
        db.commit()
        return media