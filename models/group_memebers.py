from db.database import Session_Local,BaseModel
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from datetime import datetime,UTC

class Members(BaseModel):
    __tablename__ = "members"
    member_id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.user_id"))
    group_id = Column(Integer,ForeignKey("groups.group_id"))
    role = Column(String,nullable=False,default="member")
    joined_at = Column(DateTime,default=lambda: datetime.now(UTC))

def add_member(db,uid,gid,role=None):
    member = Members(
        user_id = uid,
        group_id = gid,
        role = role
    )
    db.add(member)
    db.flush
    return member