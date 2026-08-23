from fastapi import FastAPI
from routes.websockets import ws
from routes.user import users
from routes.chats import chats

app = FastAPI()
app.include_router(ws)
app.include_router(users)
app.include_router(chats)

def get_app():
    return app 