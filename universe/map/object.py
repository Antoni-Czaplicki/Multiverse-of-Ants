import enum

from .position import Position


class ObjectTypes(enum.Enum):
    FOOD = 0
    WATER = 1
    ROCK = 2


class Object:
    def __init__(self, position: Position, object_type: ObjectTypes):
        self.position = position
        self.object_type = object_type

    def __str__(self):
        return f"({self.position}, {self.object_type})"

    def __repr__(self):
        return f"Object({self.position}, {self.object_type})"

    def interact(self, ant: "Ant"):
        if self.object_type == ObjectTypes.FOOD:
            ant.health += 10
        elif self.object_type == ObjectTypes.WATER:
            ant.health += 5
        elif self.object_type == ObjectTypes.ROCK:
            if not self.position == ant.position:
                return  # Cannot interact with the rock if the ant is not on the same position
            ant.health -= 5
            ant.position.move(ant.position.direction, -1)
        else:
            raise ValueError("Invalid object type")
