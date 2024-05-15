import asyncio
import http.server
import json
import socketserver
import threading

from websockets import ConnectionClosedError, ConnectionClosedOK
from websockets.server import serve

from universe.ants import Ant
from universe.engine import run
from universe.update import Update, UpdateType


def start_http_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()


async def handler(websocket):
    running_task = None

    async def callback(
        update_type: UpdateType, entity: Ant | None = None, target=None, state=None
    ):
        event = Update(update_type, entity, target, state).to_dict()
        try:
            await websocket.send(json.dumps(event))
        except ConnectionClosedOK:
            pass
        except ConnectionClosedError:
            pass

    config = {}
    async for message in websocket:
        data = json.loads(message)
        print(f"Received: {data}")

        print(UpdateType[data["type"]])
        if UpdateType[data["type"]] == UpdateType.SIMULATION_START:
            if running_task:
                print("Canceling running simulation")
                running_task.cancel()
            config["pause"] = False
            running_task = asyncio.create_task(run(config, callback))
        elif UpdateType[data["type"]] == UpdateType.SIMULATION_SET_BOUNDARIES:
            config["boundary"] = {"width": data["width"], "height": data["height"]}
        elif UpdateType[data["type"]] == UpdateType.SIMULATION_SET_TPS:
            config["tps"] = data["tps"]
        elif UpdateType[data["type"]] == UpdateType.SIMULATION_END:
            if running_task:
                running_task.cancel()
                running_task = None
                await websocket.send(json.dumps({"type": "SIMULATION_END"}))
                config.clear()
        elif UpdateType[data["type"]] == UpdateType.SIMULATION_PAUSE:
            if running_task:
                config["pause"] = True
                await websocket.send(json.dumps({"type": "SIMULATION_PAUSE"}))
        elif UpdateType[data["type"]] == UpdateType.SIMULATION_RESUME:
            if running_task:
                config["pause"] = False
                await websocket.send(json.dumps({"type": "SIMULATION_RESUME"}))
        else:
            print("Unknown command")


async def start_server():
    print("Connect to ws://localhost:8765")
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


threading.Thread(target=start_http_server).start()
asyncio.run(start_server())
