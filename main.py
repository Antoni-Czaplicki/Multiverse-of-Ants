import asyncio
import json

from websockets.server import serve

from universe import RNG
from universe.ants import Ant
from universe.engine import run
from universe.update import Update, UpdateType


async def handler(websocket):
    async def callback(
        update_type: UpdateType, entity: Ant | None = None, target=None, state=None
    ):
        event = Update(update_type, entity, target, state).to_dict()
        await websocket.send(json.dumps(event))

    RNG.set_seed(1234)
    await run(callback)


async def start_server():
    print("Connect to ws://localhost:8765")
    async with serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(start_server())
