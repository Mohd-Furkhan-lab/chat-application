from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from db.database import BaseModel,Session_Local
from datetime import datetime,UTC

class Messages(BaseModel):
    __tablename__ = "msg"
    msg_id = Column(Integer,primary_key=True,autoincrement=True)
    convo_id = Column(Integer,ForeignKey("convo.convo_id",ondelete="CASCADE"))
    msg = Column(String,nullable=False)
    timestamp = Column(DateTime,default=lambda: datetime.now(UTC))


def get_msg(convo_id):
    with Session_Local() as db:
        msgs = db.query(Messages).filter(Messages.convo_id == convo_id).all()
        return msgs

def add_msg(convo_id,msg):
    with Session_Local() as db:
        msg = Messages(
            convo_id = convo_id,
            msg = msg
        )
        db.add(msg)
        db.commit()


    