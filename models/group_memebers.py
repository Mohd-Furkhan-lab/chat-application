from db.database import Session_Local,BaseModel
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from datetime import datetime,UTC
from models.users import User

class Members(BaseModel):
    __tablename__ = "members"
    member_id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.user_id"))
    group_id = Column(Integer,ForeignKey("groups.group_id"))
    role = Column(String,nullable=False,default="member")
    joined_at = Column(DateTime,default=lambda: datetime.now(UTC))

def get_members(gid):
    with Session_Local() as db:
        members = (
            db.query(User.user_name)
            .join(Members, Members.user_id == User.user_id)
            .filter(Members.group_id == gid)
            .all()
        )
        return members

def add_member(db,uid,gid,role=None):
    member = Members(
        user_id = uid,
        group_id = gid,
        role = role
    )
    db.add(member)
    db.flush
    return member

def remove_user(gid,uid):
    with Session_Local() as db:
        group = db.query(Members).filter(Members.group_id == gid,Members.user_id == uid).first()
        db.delete(group)
        db.commit()

def calculate_no_members(db,gid):
    count = db.query(Members).filter(Members.group_id == gid).count()
    return count