import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

from termcolor import colored

from universe import RNG
from universe.map.position import Direction, Position

from .ants import BlackAnt, RedAnt
from .ants.ant import Ant, Role
from .map.boundary import Boundary
from .map.nest import Nest
from .map.object import Object, ObjectType
from .update import UpdateType

SIZE = 150

ROUNDS = 200

ANTS = 150
OBJECTS = 150

TPS = 20

PAUSE = 1 / TPS if TPS > 0 else 0


def print_map(ants):
    for y in range(Boundary.y, Boundary.y + Boundary.height):
        for x in range(Boundary.x, Boundary.x + Boundary.width):
            ant = None
            on_color = None
            for e in ants:
                if e.position.x == x and e.position.y == y:
                    if ant is not None:
                        on_color = "on_yellow"
                    ant = e
            if ant is not None:
                color = {
                    BlackAnt: "blue",
                    RedAnt: "red",
                }[type(ant)]
                print(
                    colored(
                        ant.position.direction.to_arrow(),
                        color=color,
                        on_color=on_color,
                        force_color="True",
                    ),
                    end=" ",
                )
                ant = None
                on_color = None
            else:
                print("_", end=" ")
        print()
    print("\n")


async def create_ant(ant_type: type, ants: Dict[Tuple[int, int], List[Ant]]) -> None:
    """Helper function to create an ant and append it to ants list."""
    new_ant = ant_type(
        Position(
            RNG.randint(Boundary.x, Boundary.x + Boundary.width),
            RNG.randint(Boundary.y, Boundary.y + Boundary.height),
            RNG.choice(list(Direction)),
        )
    )
    ants[(new_ant.position.x, new_ant.position.y)].append(new_ant)


async def create_random_object(
    objects: Dict[Tuple[int, int], List[Object]], update_callback: Callable
) -> None:
    """Helper function to create an object and append it to objects list."""
    new_object = Object(
        Position(
            RNG.randint(Boundary.x, Boundary.x + Boundary.width),
            RNG.randint(Boundary.y, Boundary.y + Boundary.height),
        ),
        RNG.choice([ObjectType.ROCK] + [ObjectType.FOOD] * 3 + [ObjectType.WATER] * 2),
    )
    objects[(new_object.position.x, new_object.position.y)].append(new_object)
    await update_callback(UpdateType.OBJECT_SPAWN, target=new_object)


async def initial_spawn(
    ants: Dict[Tuple[int, int], List[Ant]],
    nests: List[Nest],
    objects: Dict[Tuple[int, int], List[Object]],
    update_callback: Callable,
) -> None:
    """Initial spawn of ants, nests and objects in the universe."""
    for _ in range(ANTS // 3):
        await create_ant(BlackAnt, ants)
        await create_ant(BlackAnt, ants)
        await create_ant(RedAnt, ants)
    nest_1 = Nest(Nest.generate_random_nest_area())
    await update_callback(UpdateType.NEST_SPAWN, target=nest_1)
    nest_2 = Nest(Nest.generate_random_nest_area(min_distance_from=nest_1.area))
    await update_callback(UpdateType.NEST_SPAWN, target=nest_2)

    queen_1 = BlackAnt(
        Position(
            RNG.randint(nest_1.area.position_1.x, nest_1.area.position_2.x),
            RNG.randint(nest_1.area.position_1.y, nest_1.area.position_2.y),
            Direction.NORTH,
        )
    )
    queen_2 = RedAnt(
        Position(
            RNG.randint(nest_2.area.position_1.x, nest_2.area.position_2.x),
            RNG.randint(nest_2.area.position_1.y, nest_2.area.position_2.y),
            Direction.NORTH,
        )
    )

    await queen_1.set_role(Role.QUEEN, update_callback)
    nest_1.queen = queen_1
    await queen_2.set_role(Role.QUEEN, update_callback)
    nest_2.queen = queen_2

    nests.append(nest_1)
    nests.append(nest_2)
    ants[(queen_1.position.x, queen_1.position.y)].append(queen_1)
    ants[(queen_2.position.x, queen_2.position.y)].append(queen_2)

    for i in range(OBJECTS):
        await create_random_object(objects, update_callback)


async def run(update_callback: Optional[Callable] = None) -> None:
    """Run the simulation."""
    await update_callback(UpdateType.SIMULATION_START)
    Boundary.set_boundary_by_size(SIZE)
    print(
        f"Boundary: \n-x: {Boundary.x}\n-y: {Boundary.y}\nx: {Boundary.x + Boundary.width}\ny: {Boundary.y + Boundary.height}\n"
    )

    ants: Dict[Tuple[int, int], List[Ant]] = defaultdict(list)
    objects: Dict[Tuple[int, int], List[Object]] = defaultdict(list)

    nests: List[Nest] = []

    await initial_spawn(ants, nests, objects, update_callback)

    last_timestamp = datetime.now()
    await update_callback(UpdateType.SIMULATION_SET_TPS, state=TPS)
    for i in range(ROUNDS):
        for ant_row in list(ants.values()):
            for ant in ant_row:
                if ant.is_alive():
                    await ant.move(ants, nests, objects, update_callback)
                if ant.is_alive():
                    await ant.process(ants, nests, objects, update_callback)
                if not ant.is_alive() and ant in ants[(ant.position.x, ant.position.y)]:
                    ants[(ant.position.x, ant.position.y)].remove(ant)

        for _ in range(RNG.randint(0, 15)):
            await create_random_object(objects, update_callback)

        temp_tps = round(
            1 / (datetime.now() - last_timestamp).total_seconds()
            if (datetime.now() - last_timestamp).total_seconds() > 0
            else 0
        )
        if temp_tps == 0 or temp_tps > TPS:
            temp_tps = TPS
        await update_callback(UpdateType.SIMULATION_TPS, state=temp_tps)
        pause_time = (
            PAUSE - (datetime.now() - last_timestamp).total_seconds()
            if PAUSE - (datetime.now() - last_timestamp).total_seconds() > 0
            else 0
        )
        if pause_time > 0:
            await asyncio.sleep(pause_time)
        last_timestamp = datetime.now()

        # print_map(ants_old)

    print("Game over!")
    await update_callback(UpdateType.SIMULATION_END)
