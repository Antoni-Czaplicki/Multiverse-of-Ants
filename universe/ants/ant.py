import enum

from universe.map.object import Object
from universe.map.position import Direction, Position
from universe.rng import RNG
from universe.update import UpdateType


class Role(enum.Enum):
    WORKER = 0
    SOLDIER = 1
    QUEEN = 2


class Ant:
    NEXT_ID = 0

    role: Role = Role.WORKER
    health = 30
    damage = 10
    speed = 3
    position: Position = None
    alive = True

    def __init__(self, position: Position):
        self.id = Ant.NEXT_ID
        Ant.NEXT_ID += 1
        self.position = position

    def __str__(self):
        return f"({self.position}, {self.role})"

    def available_directions(self):
        return [
            direction for direction in Direction if self.position.can_move(direction)
        ]

    async def move(self, update_callback):
        available_directions = self.available_directions()
        if available_directions:
            self.position.move(RNG.choice(available_directions), RNG.randint(0, self.speed))
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

    async def attack(self, other, update_callback):
        other.health -= self.damage
        await update_callback(UpdateType.ANT_ATTACK, self, other)
        if other.health <= 0:
            await other.die(update_callback)

    async def die(self, update_callback):
        self.alive = False
        self.health = 0
        self.damage = 0
        self.speed = 0
        await update_callback(UpdateType.ANT_DEATH, self)

    def is_alive(self):
        return self.alive

    async def process(self, entities, update_callback):
        targets = [
            entity
            for entity in entities
            if entity.position
            in [
                self.position,
                self.position.calculate_new_position(self.position.direction, 1),
            ]
        ]

        for entity in targets:
            if issubclass(type(entity), Ant):
                if entity.is_alive():
                    if type(entity) is not type(self):
                        await entity.attack(self, update_callback)
                        print(f"{self} attacked {entity}")
                else:
                    if entity.role == Role.SOLDIER and self.role == Role.WORKER:
                        await self.promote(update_callback)
                    elif entity.role == Role.QUEEN and self.role == Role.SOLDIER:
                        await self.promote(update_callback)
            elif issubclass(type(entity), Object):
                await entity.interact(self, update_callback)
                entities.remove(entity)

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
