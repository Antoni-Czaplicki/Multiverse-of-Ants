import enum
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, List

from universe.map import Direction, Object, Position
from universe.update import UpdateType

if TYPE_CHECKING:
    from universe.map.boundary import Boundary
    from universe.universe import Universe


class Role(enum.Enum):
    """Enum class for ant roles."""

    WORKER = 0
    SOLDIER = 1
    QUEEN = 2


class Ant:
    """
    Class representing an ant in the universe.

    :var id: The ID of the ant.
    :type id: int
    :var role: The role of the ant.
    :type role: Role
    :var health: The health of the ant.
    :type health: int
    :var food: The food of the ant.
    :type food: int
    :var damage: The damage of the ant.
    :type damage: int
    :var speed: The speed of the ant.
    :type speed: int
    :var position: The position of the ant.
    :type position: Position
    :var alive: Whether the ant is alive.
    :type alive: bool
    """

    NEXT_ID = 0
    role: Role = Role.WORKER
    health = 50
    food = 60
    damage = 10
    speed = 3
    position: Position = None
    alive = True

    def __init__(self, position: Position):
        """
        Initialize the ant.

        :param position: The position of the ant.
        :type position: Position
        """

        self.id = Ant.NEXT_ID
        Ant.NEXT_ID += 1
        self.position = position

    def __str__(self) -> str:
        """Return the string representation of the ant."""
        return f"({self.position}, {self.role})"

    def available_directions(self, boundary: "Boundary") -> List[Direction]:
        """
        Return the available directions for the ant to move.

        :param boundary: The boundary of the universe.
        :type boundary: Boundary
        :return: The available directions for the ant to move.
        :rtype: List[Direction]
        """
        return [
            direction
            for direction in Direction
            if self.position.can_move(boundary, direction)
        ]

    @abstractmethod
    async def move(self, universe: "Universe", update_callback: Callable):
        """
        Move the ant in the universe.

        This method should be implemented by the subclasses.

        :param universe: The universe.
        :type universe: Universe
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
        pass

    async def __promote(self, update_callback: Callable, silent=False):
        """
        Promote the ant to the next role.

        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        :param silent: Whether to suppress the update, defaults to False.
        :type silent: bool
        """
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

    async def set_role(self, role: Role, update_callback: Callable):
        """
        Set the role of the ant.

        :param role: The role to set.
        :type role: Role
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
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

    async def attack(self, other: "Ant", update_callback: Callable):
        """
        Attack another ant.

        :param other: The ant to attack.
        :type other: Ant
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
        other.health -= self.damage
        await update_callback(UpdateType.ANT_ATTACK, self, other)
        if other.health <= 0:
            await other.die(update_callback)

    async def die(self, update_callback: Callable):
        """
        Kill the ant.

        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
        self.alive = False
        self.health = 0
        self.food = 0
        self.damage = 0
        self.speed = 0
        await update_callback(UpdateType.ANT_DEATH, self)

    def is_alive(self) -> bool:
        """
        Return whether the ant is alive.

        :return: True if the ant is alive, False otherwise.
        :rtype: bool
        """
        return self.alive

    async def spawn_ants(
        self,
        universe: "Universe",
        max_count: int,
        update_callback: Callable,
    ):
        """
        Spawn new ants for the queen.

        :param universe: The universe.
        :type universe: Universe
        :param max_count: The maximum number of ants to spawn.
        :type max_count: int
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
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
                        await new_ant.__promote(update_callback, silent=True)
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
                                await new_ant.__promote(update_callback, silent=True)

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
        """
        Process the ant.

        :param universe: The universe.
        :type universe: Universe
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
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
                        await self.__promote(update_callback)
                    elif entity.role == Role.QUEEN and self.role == Role.SOLDIER:
                        await self.__promote(update_callback)
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
        """
        Return a dictionary representation of the ant.

        :return: The dictionary representation of the ant.
        :rtype: dict
        """
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
