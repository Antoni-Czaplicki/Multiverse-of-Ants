import enum
import math
from functools import cache
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .boundary import Boundary


class Direction(enum.Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

    @staticmethod
    def from_angle(angle: int) -> "Direction":
        """Convert an angle to a direction."""
        return Direction((angle + 45) % 360 // 90)

    def to_angle(self) -> int:
        """Convert the direction to an angle."""
        return self.value

    def to_arrow(self) -> str:
        """Convert the direction to an arrow."""
        return {
            Direction.NORTH: "↑",
            Direction.EAST: "→",
            Direction.SOUTH: "↓",
            Direction.WEST: "←",
        }[self]


class Position:
    def __init__(self, x: int, y: int, direction: Direction = Direction.NORTH):
        """Initialize a position."""
        self.x = x
        self.y = y
        self.direction = direction

    def __add__(self, other: "Position") -> "Position":
        """Add two positions."""
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        """Subtract two positions."""
        return Position(self.x - other.x, self.y - other.y)

    def __eq__(self, other: "Position") -> bool:
        """Check if two positions are equal."""
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: "Position") -> bool:
        """Check if two positions are not equal."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the position."""
        return hash((self.x, self.y))

    def __str__(self) -> str:
        """Get a string representation of the position."""
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Get a formal string representation of the position."""
        return f"Position({self.x}, {self.y})"

    def __iter__(self) -> Tuple[int, int]:
        """Iterate over the position."""
        yield from (self.x, self.y)

    def __getitem__(self, index: int) -> int:
        """Get an item from the position."""
        return (self.x, self.y)[index]

    def manhattan_distance(self, other: "Position") -> int:
        """Calculate the Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance(self, other: "Position") -> float:
        """Calculate the Euclidean distance to another position."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def chebyshev_distance(self, other: "Position") -> int:
        """Calculate the Chebyshev distance to another position."""
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def get_neighbors(self, distance: int = 1) -> list["Position"]:
        """Get the neighbors of the position."""
        return [
            Position(self.x + dx, self.y + dy)
            for dx in range(-distance, distance + 1)
            for dy in range(-distance, distance + 1)
            if dx != 0 or dy != 0
        ]

    def direction_to(self, other):
        """Get the direction to another position."""
        return (other - self).normalize()

    @cache
    def calculate_new_position(
        self, boundary: "Boundary", direction: Direction, distance: int = 1
    ) -> "Position":
        """Calculate a new position based on a direction and distance."""
        if direction == Direction.NORTH:
            return Position(self.x, min(self.y + distance, boundary.position_2.y))
        elif direction == Direction.EAST:
            return Position(min(self.x + distance, boundary.position_2.x), self.y)
        elif direction == Direction.SOUTH:
            return Position(self.x, max(self.y - distance, boundary.position_1.y))
        elif direction == Direction.WEST:
            return Position(max(self.x - distance, boundary.position_1.x), self.y)
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def move(
        self,
        boundary: "Boundary",
        direction: Direction = None,
        distance: int = 1,
        new_position: "Position" = None,
    ):
        """Move the position."""
        if new_position:
            if boundary.contains(new_position):
                self.x, self.y = new_position
            else:
                raise ValueError(f"Out of boundary: {new_position}")
            return

        new_position = self.calculate_new_position(boundary, direction, distance)

        self.direction = direction
        if boundary.contains(new_position):
            self.x, self.y = new_position
        else:
            raise ValueError(f"Out of boundary: {new_position}")

    def can_move(
        self, boundary: "Boundary", direction: Direction, distance: int = 1
    ) -> bool:
        """Check if the position can move in a direction."""
        return boundary.contains(
            self.calculate_new_position(boundary, direction, distance)
        )

    def to_dict(self) -> dict:
        """Convert the position to a dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "direction": self.direction.to_angle(),
        }
