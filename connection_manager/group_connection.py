from fastapi import WebSocketException

class GroupChat():
    def __init__(self):
        self.connections = {}

    def add_connection(self, groupname, username, websocket):
        if groupname not in self.connections:
            self.connections[groupname] = {}
        self.connections[groupname][username] = websocket

    def remove_connection(self,groupname,username):
        group = self.connections[groupname]
        group.pop(username)

    async def braodcast_msg(self,groupname,json):
        if groupname in self.connections:
            group = self.connectionsp[groupname]
            for ws in list[group.values()]:
                await ws.send_json(json)



group_manager = GroupChat()
