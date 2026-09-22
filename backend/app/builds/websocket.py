from fastapi import WebSocket

from app.builds.events import BuildEvent


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(
        self,
        build_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if build_id not in self.active_connections:
            self.active_connections[build_id] = []

        self.active_connections[build_id].append(websocket)

    def disconnect(
        self,
        build_id: int,
        websocket: WebSocket,
    ):
        connections = self.active_connections.get(build_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.active_connections[build_id]

    async def broadcast(
        self,
        build_id: int,
        message: BuildEvent,
    ):
        connections = self.active_connections.get(
            build_id,
            [],
        )

        for websocket in connections:
            await websocket.send_json(message)


manager = ConnectionManager()
