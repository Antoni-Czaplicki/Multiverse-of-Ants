import enum
from typing import TYPE_CHECKING, Callable, List

from universe.map import Direction, Object, ObjectType, Position
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
    health = 30
    food = 50
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

    async def move(
        self,
        universe: "Universe",
        update_callback: Callable,
    ) -> None:
        available_directions = self.available_directions(universe.boundary)
        if available_directions:
            # Combine direction and distance into a single choice
            direction_distance = [
                {
                    "direction": universe.rng.choice(available_directions),
                    "distance": universe.rng.randint(0, self.speed),
                }
            ]

            # Call get_entity_positions once and store its result
            # entity_positions = self.get_other_entity_positions(ants)

            # Use the stored entity_positions in the list comprehension
            proposed_positions = [
                {"new_position": position}
                for position in self.position.get_neighbors(self.speed)
                if (
                    (position.x, position.y) in universe.ants
                    and any(
                        type(ant) is not type(self)
                        for ant in universe.ants[(position.x, position.y)]
                    )
                )
                or (
                    (position.x, position.y) in universe.objects
                    and universe.objects[(position.x, position.y)]
                    and universe.objects[(position.x, position.y)][0].object_type
                    is not ObjectType.ROCK
                )
            ]

            if self.role == Role.QUEEN:
                nearest_nest = min(
                    universe.nests,
                    key=lambda nest: nest.area.smallest_distance(self.position),
                )
                direction_to_nest = nearest_nest.area.direction_from_position(
                    self.position
                )
                if (
                    direction_to_nest is not None
                    and self.position not in nearest_nest.area
                ):
                    distance_to_nest = nearest_nest.area.smallest_distance(
                        self.position
                    )
                    direction_distance.append(
                        {
                            "direction": direction_to_nest,
                            "distance": min(abs(distance_to_nest), self.speed),
                        }
                    )
                    direction_distance.append(
                        {
                            "direction": direction_to_nest,
                            "distance": min(abs(distance_to_nest), self.speed),
                        }
                    )
                    direction_distance.append(
                        {
                            "direction": direction_to_nest,
                            "distance": min(abs(distance_to_nest), self.speed),
                        }
                    )
                    direction_distance.append(
                        {
                            "direction": direction_to_nest,
                            "distance": min(abs(distance_to_nest), self.speed),
                        }
                    )
                    direction_distance.append(
                        {
                            "direction": direction_to_nest,
                            "distance": min(abs(distance_to_nest), self.speed),
                        }
                    )
            chosen_move = universe.rng.choice(
                direction_distance + proposed_positions * 2
            )  # Double the weight of proposed_positions
            self.position.move(universe.boundary, **chosen_move)
            if self.food > 0:
                self.food -= 1
            else:
                self.health -= 1
                if self.health <= 0:
                    await self.die(update_callback)
                    return  # When the ant dies, it should not move
            await update_callback(UpdateType.ANT_MOVE, self)

    async def promote(self, update_callback):
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
                        self.food += 1
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
