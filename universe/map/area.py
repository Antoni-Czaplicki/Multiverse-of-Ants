from typing import Union

from .position import Direction, Position


class Area:
    def __init__(self, position_1: Position, position_2: Position):
        """
        Initialize an area.

        :param position_1: The first position.
        :type position_1: Position
        :param position_2: The second position.
        :type position_2: Position
        """
        self.position_1 = position_1
        self.position_2 = position_2

    def __contains__(self, position: Position) -> bool:
        """
        Check if a position is within the area.

        :param position: The position to check.
        :type position: Position
        :return: True if the position is within the area, False otherwise.
        :rtype: bool
        """
        return (
            self.position_1.x <= position.x <= self.position_2.x
            and self.position_1.y <= position.y <= self.position_2.y
        )

    def __str__(self) -> str:
        """Return a string representation of the area."""
        return f"({self.position_1}, {self.position_2})"

    def __repr__(self) -> str:
        """Return a formal string representation of the area."""
        return f"Area({self.position_1}, {self.position_2})"

    def size(self) -> int:
        """
        Calculate the size of the area.

        :return: The size of the area.
        :rtype: int
        """
        return (self.position_2 - self.position_1).manhattan_distance(Position(0, 0))

    def __center(self) -> Position:
        """
        Calculate the center of the area.

        :return: The center of the area.
        :rtype: Position
        """
        center_x = (self.position_1.x + self.position_2.x) // 2
        center_y = (self.position_1.y + self.position_2.y) // 2
        return Position(center_x, center_y)

    def smallest_distance(self, other: Union[Position, "Area"]) -> float:
        """
        Calculate the smallest distance from the area to another position or area.

        :param other: The other position or area.
        :type other: Union[Position, Area]
        :return: The smallest distance.
        :rtype: float
        """
        if isinstance(other, Position):
            return self.__center().euclidean_distance(other)
        return self.__center().euclidean_distance(other.__center())

    def direction_from_position(self, position: Position) -> Union[Direction, None]:
        """
        Determine the direction from a position to the area.

        :param position: The position.
        :type position: Position
        :return: The direction from the position to the area.
        :rtype: Direction
        """
        if position.x < self.position_1.x:
            return Direction.EAST
        if position.x > self.position_2.x:
            return Direction.WEST
        if position.y < self.position_1.y:
            return Direction.NORTH
        if position.y > self.position_2.y:
            return Direction.SOUTH
        return None

    def to_dict(self) -> dict:
        """
        Convert the area to a dictionary.

        :return: The dictionary representation of the area.
        :rtype: dict
        """
        return {
            "position_1": self.position_1.to_dict(),
            "width": self.position_2.x - self.position_1.x + 1,
            "height": self.position_2.y - self.position_1.y + 1,
            "position_2": self.position_2.to_dict(),
        }
