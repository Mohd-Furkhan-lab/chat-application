from db.database import Session_Local,BaseModel
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,func
from datetime import datetime,UTC
from models.group_memebers import Members

class Group(BaseModel):
    __tablename__ = "groups"
    group_id = Column(Integer,primary_key=True,autoincrement=True)
    group_name = Column(String,unique=True)
    created_by = Column(Integer,ForeignKey("users.user_id",ondelete="CASCADE"))
    created_at = Column(DateTime,default=lambda: datetime.now(UTC))
    no_of_members = Column(Integer,nullable=False,default=0)
    type = Column(String,nullable=False)

def get_joined_groups(uid):
    with Session_Local() as db:
        groups = db.query(Group.group_name).join(Members,Group.group_id == Members.group_id).filter(Members.user_id == uid).all()
        return [group.group_name for group in groups]

def get_group(db,gid = None, gname = None,):
    if gid != None:
        group = db.query(Group).filter(Group.group_id == gid).first()
        return group
    if gname != None:
        group = db.query(Group).filter(Group.group_name == gname).first()
        return group

def create_group(db,group_name,user_id,type):
    group = Group(
        group_name = group_name,
        created_by = user_id,
        type = type
    )
    db.add(group)
    db.flush()
    return group

def remove_group(db,is_admin,gname):
    if is_admin:
        group = db.query(Group).filter(Group.group_name == gname).first()
        if group:
            db.delete(group)
            db.flush()
            return group

def update_no_of_members(db,new_count,gid):
    group = db.query(Group).filter(Group.group_id == gid).filter()
    group.no_of_members = new_count
    db.flush()

def change_type(is_admin,gname,new_type):
    if is_admin:
        with Session_Local() as db:
            group = db.query(Group).filter(Group.group_name == gname).first()
            group.type = new_type
            db.commit()
            return True
        
