from .area import Area
from .position import Position


class Boundary(Area):
    width: int = 200
    height: int = 200

    def __init__(self):
        super().__init__(Position(0, 0), Position(200, 200))

    def set_boundary(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set the boundary with the given x, y, width, and height.

        :param x: The x-coordinate of the boundary.
        :param y: The y-coordinate of the boundary.
        :param width: The width of the boundary.
        :param height: The height of the boundary.
        """
        self.position_1 = Position(x, y)
        self.position_2 = Position(x + width, y + height)
        self.width = width
        self.height = height

    def set_boundary_by_width_height(self, width: int, height: int) -> None:
        """
        Set the boundary by width and height. The x and y coordinates are set to zero.

        :param width: The width of the boundary.
        :param height: The height of the boundary.
        """
        self.position_1 = Position(0, 0)
        self.position_2 = Position(width, height)
        self.width = width
        self.height = height

    def set_boundary_by_size(self, size: int) -> None:
        """
        Set the boundary by size. The x and y coordinates are set to negative half of the size,
        and the width and height are set to the size.

        :param size: The size to set the boundary.
        """
        self.position_1 = Position(0, 0)
        self.position_2 = Position(size, size)
        self.width = size
        self.height = size

    def contains(self, position) -> bool:
        """
        Check if the given position is within the boundary.

        :param position: The position to check.
        :return: True if the position is within the boundary, False otherwise.
        """
        return super().__contains__(position)

    def size(self) -> int:
        """
        Get the size of the boundary.

        :return: The size of the boundary.
        """
        return self.width * self.height
