from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from db.database import BaseModel,Session_Local
from datetime import datetime,UTC

class Messages(BaseModel):
    __tablename__ = "msg"
    msg_id = Column(Integer,primary_key=True,autoincrement=True)
    convo_id = Column(Integer,ForeignKey("convo.convo_id",ondelete="CASCADE"))
    msg = Column(String,nullable=False)
    sender = Column(String,nullable=False)
    timestamp = Column(DateTime,default=lambda: datetime.now(UTC))


def get_msg(convo_id):
    with Session_Local() as db:
        msgs = db.query(Messages.timestamp,Messages.msg,Messages.sender).filter(Messages.convo_id == convo_id).all()
        return [
            {
                "msg": message.msg,
                "sender": message.sender,
                "timestamp": message.timestamp
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


    