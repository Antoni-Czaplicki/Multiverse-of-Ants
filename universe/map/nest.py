from typing import Optional, Type

from universe import RNG
from universe.ants import Ant

from .area import Area
from .boundary import Boundary
from .position import Position


class Nest:
    ants_per_unit_area: int = 5
    queen: Ant = None

    def __init__(self, area: Area):
        """
        Initialize the nest with the given area.

        :param area: The area of the nest.
        :type area: Area
        """
        self.area = area

    def __contains__(self, position: Position) -> bool:
        """
        Check if the given position is within the nest area.

        :param position: The position to check.
        :type position: Position
        :return: True if the position is within the nest area, False otherwise.
        :rtype: bool
        """
        return position in self.area

    def ants_type(self) -> Type[Ant]:
        """
        Get the type of the queen ant.

        :return: The type of the queen ant.
        :rtype: Type[Ant]
        """
        return type(self.queen)

    @staticmethod
    def generate_random_nest_area(
        size_from: int = 10,
        size_to: int = 20,
        min_distance: int = 40,
        min_distance_from: Optional[Area] = None,
    ) -> Area:
        """
        Generate a random nest area.

        :param size_from: The minimum size of the nest area.
        :param size_to: The maximum size of the nest area.
        :param min_distance: The minimum distance from the given area.
        :param min_distance_from: The area to keep distance from.
        :return: The generated nest area.
        :rtype: Area
        """
        for _ in range(10):
            position_1 = Position(
                RNG.randint(Boundary.x, Boundary.x + Boundary.width - size_to),
                RNG.randint(Boundary.y, Boundary.y + Boundary.height - size_to),
            )
            position_2 = Position(
                position_1.x + RNG.randint(size_from, size_to),
                position_1.y + RNG.randint(size_from, size_to),
            )
            area = Area(position_1, position_2)
            if (
                min_distance_from is None
                or area.smallest_distance(min_distance_from) >= min_distance
            ):
                return area
            print("Could not find a suitable area, trying again...")
        else:
            print("Could not find a suitable area, using random area")
            return area

    def to_dict(self) -> dict:
        """
        Convert the nest to a dictionary.

        :return: The dictionary representation of the nest.
        :rtype: dict
        """
        return {
            "area": self.area.to_dict(),
            "ants_type": self.ants_type().__name__,
        }
