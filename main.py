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

HTTP_PORT = 80


def start_http_server():
    http_handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", HTTP_PORT), http_handler) as httpd:
        print(
            f"Serving HTTP server at port {HTTP_PORT} - http://localhost:{HTTP_PORT} for local deployment"
        )
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
    try:
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
                else:
                    await websocket.send(json.dumps({"type": "SIMULATION_NOT_RUNNING"}))
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_PAUSE:
                if running_task:
                    config["pause"] = True
                    await websocket.send(json.dumps({"type": "SIMULATION_PAUSE"}))
                else:
                    await websocket.send(json.dumps({"type": "SIMULATION_NOT_RUNNING"}))
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_RESUME:
                if running_task:
                    config["pause"] = False
                    await websocket.send(json.dumps({"type": "SIMULATION_RESUME"}))
                else:
                    await websocket.send(json.dumps({"type": "SIMULATION_NOT_RUNNING"}))
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_SET_SEED:
                config["seed"] = data["seed"]
            else:
                print("Unknown command")
    except ConnectionClosedOK:
        pass
    except ConnectionClosedError:
        pass


async def start_servers():
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    try:
        http_thread.start()
        print("Connect to ws://localhost:8765")
        async with serve(handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever
    except asyncio.CancelledError:
        print("Server stopped")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Application will restart in 5 seconds")
        await asyncio.sleep(5)
        await start_servers()


asyncio.run(start_servers())
