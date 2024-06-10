import enum
from typing import TYPE_CHECKING, Callable

from .position import Position

if TYPE_CHECKING:
    from universe.ants import Ant
    from universe.map.boundary import Boundary


class ObjectType(enum.Enum):
    """Enum class for object types."""

    FOOD = 0
    WATER = 1
    ROCK = 2


class Object:
    """Class representing an object in the universe.

    :var position: The position of the object.
    :type position: Position
    :var object_type: The type of the object.
    :type object_type: ObjectType
    :var usages_left: The number of usages left for the object.
    :type usages_left: int
    """

    usages_left: int = 3

    def __init__(self, position: Position, object_type: ObjectType):
        """
        Initialize an object.

        :param position: Position of the object.
        :type position: Position
        :param object_type: Type of the object.
        :type object_type: ObjectType
        """
        self.position = position
        self.object_type = object_type

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return f"({self.position}, {self.object_type})"

    def __repr__(self) -> str:
        """Return a formal string representation of the object."""
        return f"Object({self.position}, {self.object_type})"

    async def interact(
        self, boundary: "Boundary", ant: "Ant", update_callback: Callable
    ):
        """
        Interact with an ant.

        :param boundary: The boundary of the universe.
        :type boundary: Boundary
        :param ant: The ant to interact with.
        :type ant: Ant
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
        if self.object_type == ObjectType.FOOD:
            ant.food += 7
        elif self.object_type == ObjectType.WATER:
            ant.food += 5
            ant.health += 3
        elif self.object_type == ObjectType.ROCK:
            if not self.position == ant.position:
                return  # Cannot interact with the rock if the ant is not on the same position
            ant.health -= 1
            try:
                ant.position.move(boundary, ant.position.direction, -1)
            except ValueError:
                self.usages_left = 0  # Destroy the rock if the ant is at the boundary
        else:
            raise ValueError("Invalid object type")
        self.usages_left -= 1

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary.

        :return: The dictionary representation of the object.
        :rtype: dict
        """
        return {
            "position": self.position.to_dict(),
            "type": self.object_type.name,
        }
