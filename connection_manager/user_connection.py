from fastapi import WebSocketException

class Connections():
    def __init__(self):
        self.active_connection = {}

    def add_connection(self,user_name,ws):
        self.active_connection[user_name] = ws

    def remove_connection(self,user_name):
        self.active_connection.pop(user_name)

    async def braodcast_msg(self,json,reciever):
        if reciever in self.active_connection:
            await self.active_connection[reciever].send_json(json)

manager = Connections()