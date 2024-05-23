import asyncio
from datetime import datetime
from typing import Callable, Optional

from termcolor import colored

from universe.ants import BlackAnt, RedAnt
from universe.ants.ant import Role
from universe.map.nest import Nest
from universe.map.object import Object, ObjectType
from universe.map.position import Direction, Position
from universe.universe import Universe
from universe.update import UpdateType

SIZE = 150

ROUNDS = 200

ANTS = 150
OBJECTS = 150

TPS = 20

PAUSE = 1 / TPS if TPS > 0 else 0


def print_map(ants, boundary) -> None:
    for y in range(boundary.y, boundary.y + boundary.height):
        for x in range(boundary.x, boundary.x + boundary.width):
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
                        color=color,  # type: ignore
                        on_color=on_color,
                        force_color=True,
                    ),
                    end=" ",
                )
                ant = None
                on_color = None
            else:
                print("_", end=" ")
        print()
    print("\n")


async def create_ant(
    ant_type: type, universe: Universe, update_callback: Callable
) -> None:
    """Helper function to create an ant and append it to ants list."""
    new_ant = ant_type(
        Position(
            universe.rng.randint(
                universe.boundary.x, universe.boundary.x + universe.boundary.width
            ),
            universe.rng.randint(
                universe.boundary.y, universe.boundary.y + universe.boundary.height
            ),
            universe.rng.choice(list(Direction)),
        )
    )
    universe.ants[(new_ant.position.x, new_ant.position.y)].append(new_ant)
    universe.ants_count += 1
    await update_callback(UpdateType.ANT_SPAWN, new_ant)


async def create_random_object(universe: Universe, update_callback: Callable) -> None:
    """Helper function to create an object and append it to objects list."""
    new_object = Object(
        Position(
            universe.rng.randint(
                universe.boundary.x, universe.boundary.x + universe.boundary.width
            ),
            universe.rng.randint(
                universe.boundary.y, universe.boundary.y + universe.boundary.height
            ),
        ),
        universe.rng.choice(
            [ObjectType.ROCK] + [ObjectType.FOOD] * 6 + [ObjectType.WATER] * 4
        ),
    )
    universe.objects[(new_object.position.x, new_object.position.y)].append(new_object)
    universe.objects_count += 1
    await update_callback(UpdateType.OBJECT_SPAWN, target=new_object)


async def initial_spawn(
    universe: Universe,
    update_callback: Callable,
) -> None:
    """Initial spawn of ants, nests and objects in the universe."""
    for _ in range(
        universe.rng.randint(100, max(universe.boundary.size() // 500, 123)) // 3
    ):
        await create_ant(BlackAnt, universe, update_callback)
        await create_ant(BlackAnt, universe, update_callback)
        await create_ant(RedAnt, universe, update_callback)
    nest_1 = Nest(Nest.generate_random_nest_area(universe))
    await update_callback(UpdateType.NEST_SPAWN, target=nest_1)
    nest_2 = Nest(
        Nest.generate_random_nest_area(universe, min_distance_from=nest_1.area)
    )
    await update_callback(UpdateType.NEST_SPAWN, target=nest_2)

    queen_1 = BlackAnt(
        Position(
            universe.rng.randint(nest_1.area.position_1.x, nest_1.area.position_2.x),
            universe.rng.randint(nest_1.area.position_1.y, nest_1.area.position_2.y),
            Direction.NORTH,
        )
    )
    queen_2 = RedAnt(
        Position(
            universe.rng.randint(nest_2.area.position_1.x, nest_2.area.position_2.x),
            universe.rng.randint(nest_2.area.position_1.y, nest_2.area.position_2.y),
            Direction.NORTH,
        )
    )

    await queen_1.set_role(Role.QUEEN, update_callback)
    nest_1.queen = queen_1
    await queen_2.set_role(Role.QUEEN, update_callback)
    nest_2.queen = queen_2

    universe.nests.append(nest_1)
    universe.nests.append(nest_2)
    universe.ants[(queen_1.position.x, queen_1.position.y)].append(queen_1)
    universe.ants[(queen_2.position.x, queen_2.position.y)].append(queen_2)

    for _ in range(universe.rng.randint(75, max(universe.boundary.size() // 500, 100))):
        await create_random_object(universe, update_callback)


async def run(config, update_callback: Optional[Callable] = None) -> None:
    """Run the simulation."""
    universe = Universe()

    await update_callback(UpdateType.SIMULATION_START)
    universe.rng.set_seed(config.get("seed", "0"))
    if (
        "boundary" in config
        and "width" in config["boundary"]
        and "height" in config["boundary"]
    ):
        universe.boundary.set_boundary_by_width_height(
            config["boundary"]["width"], config["boundary"]["height"]
        )
    else:
        universe.boundary.set_boundary_by_size(SIZE)
        print("Setting default boundary")
    print(
        f"universe.boundary: \n-x: {universe.boundary.x}\n-y: {universe.boundary.y}\nx: {universe.boundary.x + universe.boundary.width}\ny: {universe.boundary.y + universe.boundary.height}\n"
    )

    await initial_spawn(universe, update_callback)

    await update_callback(UpdateType.SIMULATION_SET_TPS, state=TPS)
    last_timestamp = datetime.now()

    for i in range(ROUNDS):
        while config.get("pause", False):
            await asyncio.sleep(1)
            last_timestamp = datetime.now()

        for ant_row in list(universe.ants.values()):
            for ant in ant_row:
                if ant.is_alive():
                    await ant.move(universe, update_callback)
                if ant.is_alive():
                    await ant.process(universe, update_callback)
                if (
                    not ant.is_alive()
                    and ant in universe.ants[(ant.position.x, ant.position.y)]
                ):
                    universe.ants[(ant.position.x, ant.position.y)].remove(ant)
                    universe.ants_count -= 1

        if universe.objects_count < universe.MAX_OBJECTS:
            for _ in range(
                universe.rng.randint(0, max(universe.boundary.size() // 2000, 10))
            ):
                await create_random_object(universe, update_callback)

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

        # print_map([ant for ant_row in universe.ants.values() for ant in ant_row], universe.boundary)

    print("Game over!")
    await update_callback(UpdateType.SIMULATION_END)
    print(f"Next random number: {universe.rng.randint(0, 1000)}")
    config.clear()
