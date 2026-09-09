from fastapi.websockets import WebSocket,WebSocketDisconnect
from fastapi import APIRouter
from auth.jwt_token import verify_token
from connection_manager.user_connection import manager
from connection_manager.group_connection import group_manager


ws = APIRouter(prefix="/ws")

@ws.websocket('/connect')
async def connect_websokets(ws : WebSocket):
    token = ws.cookies.get("access")
    is_logeedin = verify_token(token)
    if is_logeedin:
        manager.add_connection(is_logeedin.get("user_name"),ws)
        await ws.accept()
        try:
            while True:
                msg = await ws.receive_text()
        except WebSocketDisconnect:
            manager.remove_connection(is_logeedin.get("user_name"))


@ws.websocket('/connect/{groupname}')
async def group_connect_websokets(groupname,ws : WebSocket):
    token = ws.cookies.get("access")
    is_logeedin = verify_token(token)
    if is_logeedin:
        group_manager.add_connection(groupname,is_logeedin.get("user_name"),ws)
        await ws.accept()
        try:
            while True:
                msg = await ws.receive_text()
        except WebSocketDisconnect:
            group_manager.remove_connection(groupname,is_logeedin.get("user_name"))
