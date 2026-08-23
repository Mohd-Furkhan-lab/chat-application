from app.main import get_app
from db.database import BaseModel,engine
from models.users import User
from models.messages import Messages
from models.conversation import Conversation
from fastapi.middleware.cors import CORSMiddleware
BaseModel.metadata.create_all(engine)

app = get_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://localhost:3001",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://192.168.0.101:3000/"

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)