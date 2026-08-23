from fastapi.websockets import WebSocket
from fastapi import APIRouter
from auth.jwt_token import verify_token
from connection_manager.manage_connection import manager


ws = APIRouter(prefix="/ws")

@ws.websocket('/connect')
async def connect_websokets(ws : WebSocket):
    token = ws.cookies.get("access")
    is_logeedin = verify_token(token)
    if is_logeedin:
        manager.add_connection(is_logeedin.get("user_name"),ws)
        await ws.accept()
        while True:
            msg = await ws.receive_text()
        
