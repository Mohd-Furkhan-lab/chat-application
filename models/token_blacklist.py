from db.database import BaseModel,Session_Local
from sqlalchemy import Column,Integer,String,Boolean

class TokenBlacklist(BaseModel):
    __tablename__ = "revoked_tokens"
    id = Column(Integer,primary_key=True,autoincrement=True)
    jti = Column(String,nullable=False)
    expires_at = Column(Integer,nullable=False)
    revoked = Column(Boolean,nullable=False)


def revoketoken(jti,expires_at,revoked):
    with Session_Local() as db:
        token = TokenBlacklist(
            jti = jti,
            expires_at = expires_at,
            revoked = revoked
        )
    db.add(token)
    db.commit()
    return True

def is_revoked(jti):
    with Session_Local() as db:
        token = db.query(TokenBlacklist.jti == jti).first()
        return token