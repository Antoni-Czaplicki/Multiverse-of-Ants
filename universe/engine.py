import asyncio
from datetime import datetime

from termcolor import colored

from universe import RNG
from universe.map.position import Direction, Position

from .ants import BlackAnt, RedAnt
from .map.boundary import Boundary
from .update import UpdateType

ANTS = 150

TPS = 200

PAUSE = 1 / TPS if TPS > 0 else 0


def print_map(entities):
    for y in range(Boundary.y, Boundary.y + Boundary.height):
        for x in range(Boundary.x, Boundary.x + Boundary.width):
            entity = None
            on_color = None
            for e in entities:
                if e.position.x == x and e.position.y == y:
                    if entity is not None:
                        on_color = "on_yellow"
                    entity = e
            if entity is not None:
                color = {
                    BlackAnt: "blue",
                    RedAnt: "red",
                }[type(entity)]
                print(
                    colored(
                        entity.position.direction.to_arrow(),
                        color=color,
                        on_color=on_color,
                        force_color="True",
                    ),
                    end=" ",
                )
                entity = None
                on_color = None
            else:
                print("_", end=" ")
        print()
    print("\n")


async def run(update_callback=None):
    Boundary.set_boundary_by_size(70)
    print(
        f"Boundary: \n-x: {Boundary.x}\n-y: {Boundary.y}\nx: {Boundary.x + Boundary.width}\ny: {Boundary.y + Boundary.height}\n"
    )
    entities = []

    for i in range(ANTS // 3):
        entities.append(
            BlackAnt(
                Position(
                    RNG.randint(Boundary.x, Boundary.x + Boundary.width),
                    RNG.randint(Boundary.y, Boundary.y + Boundary.height),
                    RNG.choice(list(Direction)),
                )
            )
        )
        entities.append(
            BlackAnt(
                Position(
                    RNG.randint(Boundary.x, Boundary.x + Boundary.width),
                    RNG.randint(Boundary.y, Boundary.y + Boundary.height),
                    RNG.choice(list(Direction)),
                )
            )
        )
        entities.append(
            RedAnt(
                Position(
                    RNG.randint(Boundary.x, Boundary.x + Boundary.width),
                    RNG.randint(Boundary.y, Boundary.y + Boundary.height),
                    RNG.choice(list(Direction)),
                )
            )
        )

    last_timestamp = datetime.now()

    for i in range(200):
        for entity in entities:
            await entity.move(update_callback)
            await entity.process(entities, update_callback)
            if not entity.is_alive():
                entities.remove(entity)
            temp_tps = round(1 / (datetime.now() - last_timestamp).total_seconds() if (datetime.now() - last_timestamp).total_seconds() > 0 else 0)
            if temp_tps == 0 or temp_tps > TPS:
                temp_tps = TPS
            await update_callback(UpdateType.SIMULATION_TPS, state=temp_tps)
            await asyncio.sleep(PAUSE - (datetime.now() - last_timestamp).total_seconds() if PAUSE - (datetime.now() - last_timestamp).total_seconds() > 0 else 0)
            last_timestamp = datetime.now()


        print_map(entities)

    print("Game over!")
