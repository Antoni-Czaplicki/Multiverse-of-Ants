import enum
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, List

from universe.map import Direction, Object, Position
from universe.update import UpdateType

if TYPE_CHECKING:
    from universe.map.boundary import Boundary
    from universe.universe import Universe


class Role(enum.Enum):
    WORKER = 0
    SOLDIER = 1
    QUEEN = 2


class Ant:
    NEXT_ID = 0

    role: Role = Role.WORKER
    health = 50
    food = 60
    damage = 10
    speed = 3
    position: Position = None
    alive = True

    def __init__(self, position: Position):
        self.id = Ant.NEXT_ID
        Ant.NEXT_ID += 1
        self.position = position

    def __str__(self) -> str:
        return f"({self.position}, {self.role})"

    def available_directions(self, boundary: "Boundary") -> List[Direction]:
        return [
            direction
            for direction in Direction
            if self.position.can_move(boundary, direction)
        ]

    @abstractmethod
    async def move(self, universe: "Universe", update_callback: Callable):
        pass

    async def promote(self, update_callback, silent=False):
        if self.role == Role.WORKER:
            self.role = Role.SOLDIER
            self.health = round(self.health * 1.5)
            self.damage = round(self.damage * 1.5)
            self.speed = round(self.speed * 1.5)
        elif self.role == Role.SOLDIER:
            self.role = Role.QUEEN
            self.health *= 3
            self.damage *= 4
            self.speed = 2
        else:
            raise ValueError("Cannot promote a queen")
        if not silent:
            await update_callback(UpdateType.ANT_PROMOTE, self)

    async def set_role(self, role, update_callback):
        self.role = role
        if role == Role.SOLDIER:
            self.health = 45
            self.damage = 15
            self.speed = 4
        elif role == Role.QUEEN:
            self.health = 90
            self.food = 25
            self.damage = 40
            self.speed = 1
        await update_callback(UpdateType.ANT_PROMOTE, self)

    async def attack(self, other, update_callback):
        other.health -= self.damage
        await update_callback(UpdateType.ANT_ATTACK, self, other)
        if other.health <= 0:
            await other.die(update_callback)

    async def die(self, update_callback):
        self.alive = False
        self.health = 0
        self.food = 0
        self.damage = 0
        self.speed = 0
        await update_callback(UpdateType.ANT_DEATH, self)

    def is_alive(self):
        return self.alive

    async def spawn_ants(
        self,
        universe: "Universe",
        max_count: int,
        update_callback: Callable,
    ):
        if universe.ants_count < universe.MAX_ANTS:
            for _ in range(
                universe.rng.choice([universe.rng.randint(0, max_count), 0, 0, 0, 0])
            ):
                for direction in self.available_directions(universe.boundary):
                    new_position = self.position.calculate_new_position(
                        universe.boundary, direction, 1
                    )
                    new_ant = type(self)(new_position)
                    if universe.rng.random() < 0.05:
                        await new_ant.promote(update_callback, silent=True)
                        if universe.rng.random() < 0.02:
                            neighbors_20 = self.position.get_neighbors(5)
                            same_color_queen_in_20_count = len(
                                [
                                    ant
                                    for position in neighbors_20
                                    for ant in universe.ants.get(
                                        (position.x, position.y), []
                                    )
                                    if type(ant) is type(self)
                                ]
                            )
                            if same_color_queen_in_20_count < 3:
                                await new_ant.promote(update_callback, silent=True)

                    universe.ants[(new_ant.position.x, new_ant.position.y)].append(
                        new_ant
                    )
                    universe.ants_count += 1
                    await update_callback(UpdateType.ANT_SPAWN, new_ant)

    async def process(
        self,
        universe: "Universe",
        update_callback: Callable,
    ):
        front_position = self.position.calculate_new_position(
            universe.boundary, self.position.direction, 1
        )

        targets = (
            universe.ants.get((self.position.x, self.position.y), [])
            + universe.ants.get((front_position.x, front_position.y), [])
            + universe.objects.get((self.position.x, self.position.y), [])
            + universe.objects.get((front_position.x, front_position.y), [])
        )

        for entity in targets:
            if issubclass(type(entity), Ant):
                if entity.is_alive():
                    if type(entity) is not type(self):
                        await entity.attack(self, update_callback)
                else:
                    if entity.role == Role.SOLDIER and self.role == Role.WORKER:
                        await self.promote(update_callback)
                    elif entity.role == Role.QUEEN and self.role == Role.SOLDIER:
                        await self.promote(update_callback)
            elif issubclass(type(entity), Object):
                await entity.interact(universe.boundary, self, update_callback)
                if (
                    entity.usages_left <= 0
                    and entity
                    in universe.objects[(entity.position.x, entity.position.y)]
                ):
                    universe.objects[(entity.position.x, entity.position.y)].remove(
                        entity
                    )
                    universe.objects_count -= 1
                    await update_callback(UpdateType.OBJECT_DESPAWN, target=entity)

        if self.role is Role.QUEEN:
            # check if queen is in nest
            for nest in universe.nests:
                if self.position in nest.area:
                    if self.food < 10:
                        self.food += 2
                    if self.health < 90:
                        self.health += 3
                    neighbors_5 = self.position.get_neighbors(5)
                    same_color_ants_in_5_count = len(
                        [
                            ant
                            for position in neighbors_5
                            for ant in universe.ants.get((position.x, position.y), [])
                            if type(ant) is type(self)
                        ]
                    )
                    nest.queen = self
                    if same_color_ants_in_5_count < 20:
                        await self.spawn_ants(universe, 3, update_callback)
                    break

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role.name,
            "color": {
                "BlackAnt": "black",
                "RedAnt": "red",
            }[type(self).__name__],
            "health": self.health,
            "damage": self.damage,
            "speed": self.speed,
            "position": self.position.to_dict(),
            "alive": self.alive,
        }
