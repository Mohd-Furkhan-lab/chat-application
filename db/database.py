from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os

load_dotenv()


database_url = os.getenv("database_url")

engine = create_engine(database_url)

Session_Local = sessionmaker(bind=engine)

BaseModel = declarative_base()

