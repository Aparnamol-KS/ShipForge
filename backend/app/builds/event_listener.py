# take Redis events and forward them to a connected WebSocket.

import asyncio

from fastapi import WebSocket

from app.redis_client.subscriber import get_build_event


async def forward_build_events(
    build_id: int,
    websocket: WebSocket,
) -> None:
    while True:
        event = await asyncio.to_thread(
            get_build_event,
            build_id,
            1,
        )

        if event is None:
            continue

        await websocket.send_json(event)

        if event.get("type") == "status" and event.get("status") in {
            "success",
            "failed",
        }:
            break