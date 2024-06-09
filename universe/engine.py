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
from universe.utils import save_statistics_to_csv

DEFAULT_SIZE = 150

DEFAULT_ROUNDS = 200

ANTS = 150
OBJECTS = 150

DEFAULT_TPS = 20


def print_map(ants, boundary) -> None:
    width = boundary.width
    height = boundary.height

    grid = [["_" for _ in range(width)] for _ in range(height)]

    color_map = {
        BlackAnt: "blue",
        RedAnt: "red",
    }

    for ant in ants:
        x, y = (
            ant.position.x - boundary.position_1.x,
            ant.position.y - boundary.position_1.y,
        )
        if grid[y][x] == "_":
            grid[y][x] = colored(
                ant.position.direction.to_arrow(),
                color=color_map[type(ant)],
                force_color=True,
            )
        else:
            grid[y][x] = colored(
                ant.position.direction.to_arrow(),
                color=color_map[type(ant)],
                on_color="on_yellow",
                force_color=True,
            )

    for row in grid:
        print("".join(row))
    print("\n")


async def create_ant(
    ant_type: type, universe: Universe, update_callback: Callable
) -> None:
    """Helper function to create an ant and append it to ants list."""
    new_ant = ant_type(
        Position(
            universe.rng.randint(
                universe.boundary.position_1.x, universe.boundary.position_2.x
            ),
            universe.rng.randint(
                universe.boundary.position_1.y, universe.boundary.position_2.y
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
                universe.boundary.position_1.x, universe.boundary.position_2.x
            ),
            universe.rng.randint(
                universe.boundary.position_1.y, universe.boundary.position_2.y
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
    tps = config.get("tps", DEFAULT_TPS)
    pause = 1 / tps if tps > 0 else 0
    rounds = config.get("rounds", DEFAULT_ROUNDS)
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
        universe.boundary.set_boundary_by_size(DEFAULT_SIZE)
        print("Setting default boundary")
    print(
        f"universe.boundary: \n-x: {universe.boundary.position_1.x}\n-y: {universe.boundary.position_1.y}\nx: {universe.boundary.position_2.x}\ny: {universe.boundary.position_2.y}\n"
    )

    await initial_spawn(universe, update_callback)

    await update_callback(UpdateType.SIMULATION_SET_TPS, state=tps)
    last_timestamp = datetime.now()

    current_round = 1

    while rounds >= current_round:
        while config.get("pause", False):
            await asyncio.sleep(0.1)
            last_timestamp = datetime.now()
        if "tps" in config and config.get("tps", 20) != tps:
            tps = config.get("tps", 20)
            pause = 1 / tps if tps > 0 else 0
        if "rounds" in config and config.get("rounds", 200) != rounds:
            rounds = config.get("rounds", 200)

        if current_round % 20 == 0:
            save_statistics_to_csv(
                [ant for ant_row in universe.ants.values() for ant in ant_row],
                "statistics.csv",
                current_round,
            )
        while config.get("pause", False):
            await asyncio.sleep(1)
            last_timestamp = datetime.now()
        await update_callback(UpdateType.SIMULATION_CURRENT_ROUND, state=current_round)

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
        if temp_tps == 0 or temp_tps > tps:
            temp_tps = tps
        await update_callback(UpdateType.SIMULATION_TPS, state=temp_tps)
        pause_time = (
            pause - (datetime.now() - last_timestamp).total_seconds()
            if pause - (datetime.now() - last_timestamp).total_seconds() > 0
            else 0
        )
        if pause_time > 0:
            await asyncio.sleep(pause_time)
        last_timestamp = datetime.now()

        if config.get("console_map", False):
            print_map(
                [ant for ant_row in universe.ants.values() for ant in ant_row],
                universe.boundary,
            )

        current_round += 1

    print("Game over!")
    await update_callback(UpdateType.SIMULATION_END)
    print(f"Next random number: {universe.rng.randint(0, 1000)}")
    config.clear()
