import asyncio
import http.server
import json
import socketserver
import threading
from concurrent.futures import ThreadPoolExecutor

import keyboard
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
                if "tps" in data and isinstance(data["tps"], int) and data["tps"] > 0:
                    config["tps"] = data["tps"]
                else:
                    await websocket.send(json.dumps({"type": "ERROR_INVALID_TPS"}))
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_SET_ROUNDS:
                if (
                    "rounds" in data
                    and isinstance(data["rounds"], int)
                    and data["rounds"] > 0
                ):
                    config["rounds"] = data["rounds"]
                else:
                    await websocket.send(json.dumps({"type": "ERROR_INVALID_ROUNDS"}))
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_END:
                if running_task:
                    running_task.cancel()
                    running_task = None
                    await websocket.send(json.dumps({"type": "SIMULATION_END"}))
                    config.clear()
                else:
                    await websocket.send(
                        json.dumps({"type": "ERROR_SIMULATION_NOT_RUNNING"})
                    )
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_PAUSE:
                if running_task:
                    config["pause"] = True
                    await websocket.send(json.dumps({"type": "SIMULATION_PAUSE"}))
                else:
                    await websocket.send(
                        json.dumps({"type": "ERROR_SIMULATION_NOT_RUNNING"})
                    )
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_RESUME:
                if running_task:
                    config["pause"] = False
                    await websocket.send(json.dumps({"type": "SIMULATION_RESUME"}))
                else:
                    await websocket.send(
                        json.dumps({"type": "ERROR_SIMULATION_NOT_RUNNING"})
                    )
            elif UpdateType[data["type"]] == UpdateType.SIMULATION_SET_SEED:
                config["seed"] = data["seed"]
            else:
                print("Unknown command")
    except ConnectionClosedOK:
        pass
    except ConnectionClosedError:
        pass


# This is a dummy function that does nothing and is used to replace the update_callback in the run function
async def do_nothing(*args, **kwargs):
    pass


executor = ThreadPoolExecutor(max_workers=1)


def run_simulation(running_task, config):
    if running_task:
        print("Canceling running simulation")
        running_task.cancel()
    config["pause"] = False
    executor.submit(asyncio.run, run(config, do_nothing))


def stop_simulation(running_task):
    if running_task:
        print("Canceling running simulation")
        running_task.cancel()


def start_console_mode():
    print("Console mode started")
    keyboard.remove_hotkey("ctrl+shift+w")
    running_task = None
    config = {}
    keyboard.add_hotkey("ctrl+shift+s", run_simulation, args=(running_task, config))
    keyboard.add_hotkey("ctrl+shift+x", stop_simulation, args=(running_task,))
    keyboard.add_hotkey(
        "ctrl+shift+d",
        lambda: config.update({"console_map": not config.get("console_map", False)}),
    )
    print("Press ctrl+shift+s to start simulation")
    print("Press ctrl+shift+x to stop simulation")
    print("Press ctrl+shift+d to toggle console map of ants")


async def start_servers():
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    try:
        http_thread.start()
        print("Connect to ws://localhost:8765")
        # Allow to start the simulation without opening the browser
        keyboard.add_hotkey("ctrl+shift+w", start_console_mode)
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
