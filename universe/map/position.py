import enum
import math

from universe.map.boundary import Boundary


class Direction(enum.Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

    @staticmethod
    def from_angle(angle):
        return Direction((angle + 45) % 360 // 90)

    def to_angle(self):
        return self.value

    def to_arrow(self):
        return {
            Direction.NORTH: "↑",
            Direction.EAST: "→",
            Direction.SOUTH: "↓",
            Direction.WEST: "←",
        }[self]


class Position:
    def __init__(self, x: int, y: int, direction: Direction = Direction.NORTH):
        self.x = x
        self.y = y
        self.direction = direction

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Position({self.x}, {self.y})"

    def __lt__(self, other):
        return self.x < other.x or (self.x == other.x and self.y < other.y)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return self.x > other.x or (self.x == other.x and self.y > other.y)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __len__(self):
        return 2

    def __copy__(self):
        return Position(self.x, self.y)

    def __deepcopy__(self, memo):
        return Position(self.x, self.y)

    def manhattan_distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def chebyshev_distance(self, other):
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def get_neighbors(self, distance=1):
        return [
            Position(self.x + dx, self.y + dy)
            for dx in range(-distance, distance + 1)
            for dy in range(-distance, distance + 1)
            if dx != 0 or dy != 0
        ]

    def direction_to(self, other):
        return (other - self).normalize()

    def calculate_new_position(self, direction: Direction, distance: int = 1):
        if direction == Direction.NORTH:
            return Position(
                self.x, min(self.y + distance, Boundary.y + Boundary.height - 1)
            )
        elif direction == Direction.EAST:
            return Position(
                min(self.x + distance, Boundary.x + Boundary.width - 1), self.y
            )
        elif direction == Direction.SOUTH:
            return Position(self.x, max(self.y - distance, Boundary.y))
        elif direction == Direction.WEST:
            return Position(max(self.x - distance, Boundary.x), self.y)
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def move(self, direction: Direction, distance: int = 1):
        self.direction = direction
        # print(f"Moving {distance} steps {direction} from {self}")
        new_position = self.calculate_new_position(direction, distance)

        if Boundary.contains(new_position):
            self.x = new_position.x
            self.y = new_position.y
        else:
            raise ValueError(f"Out of boundary: {new_position}")

    def can_move(self, direction: Direction, distance: int = 1):
        new_position = self.calculate_new_position(direction, distance)

        return Boundary.contains(new_position)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "direction": self.direction.to_angle(),
        }
