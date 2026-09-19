from sqlalchemy import Column, String, Integer, ForeignKey, DateTime,Enum
from config.database  import BaseModel, Session_Local
from datetime import datetime, UTC
from utlis.media_types import MediaType

class GroupMessages(BaseModel):
    __tablename__ = "group_msg"
    msg_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.group_id", ondelete="CASCADE"))
    sender = Column(String, nullable=False)
    msg = Column(String, nullable=True)
    media_url = Column(String,nullable=True)
    media_type = Column(Enum(MediaType),nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))


def get_group_msgs(db,group_id):
        msgs = (
            db.query(GroupMessages.timestamp, GroupMessages.msg, GroupMessages.sender, GroupMessages.media_url, GroupMessages.media_type)
            .filter(GroupMessages.group_id == group_id)
            .order_by(GroupMessages.timestamp)
            .all()
        )
        return [
            {"msg": m.msg, "sender": m.sender, "timestamp": m.timestamp, "media_url" :m.media_url, "media_type" : m.media_type}
            for m in msgs
        ]


def add_group_msg(db,group_id, sender, msg):
    new_msg = GroupMessages(
            group_id=group_id,
            sender=sender,
            msg=msg
        )
    db.add(new_msg)
    db.flush()
    return True

def add_group_media(db,group_id, sender, url, type):
    new_msg = GroupMessages(
            group_id=group_id,
            sender=sender,
            media_url = url,
            media_type = type
        )
    db.add(new_msg)
    db.flush()
    return True


def delete_group_msgs(db, group_id):
    db.query(GroupMessages).filter(GroupMessages.group_id == group_id).delete()
    return True