from .area import Area
from .position import Position


class Boundary(Area):
    """
    Class representing the boundary of the universe.

    :var width: The width of the boundary.
    :type width: int
    """

    width: int = 200
    height: int = 200

    def __init__(self):
        """
        Initialize the boundary.
        """
        super().__init__(Position(0, 0), Position(199, 199))

    def __set_boundary(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set the boundary with the given x, y, width, and height.

        :param x: The x-coordinate of the boundary.
        :type x: int
        :param y: The y-coordinate of the boundary.
        :type y: int
        :param width: The width of the boundary.
        :type width: int
        :param height: The height of the boundary.
        :type height: int
        """
        self.position_1 = Position(x, y)
        self.position_2 = Position(x + width - 1, y + height - 1)
        self.width = width
        self.height = height

    def set_boundary_by_width_height(self, width: int, height: int) -> None:
        """
        Set the boundary by width and height. The x and y coordinates are set to zero.

        :param width: The width of the boundary.
        :type width: int
        :param height: The height of the boundary.
        :type height: int
        """
        self.position_1 = Position(0, 0)
        self.position_2 = Position(width - 1, height - 1)
        self.width = width
        self.height = height

    def set_boundary_by_size(self, size: int) -> None:
        """
        Set the boundary by size.

        The x and y coordinates are set to negative half of the size, and the width and height are set to the size.

        :param size: The size to set the boundary.
        :type size: int
        """
        self.position_1 = Position(0, 0)
        self.position_2 = Position(size - 1, size - 1)
        self.width = size
        self.height = size

    def contains(self, position) -> bool:
        """
        Check if the given position is within the boundary.

        :param position: The position to check.
        :type position: Position
        :return: True if the position is within the boundary, False otherwise.
        :rtype: bool
        """
        return super().__contains__(position)

    def size(self) -> int:
        """
        Get the size of the boundary.

        :return: The size of the boundary.
        :rtype: int
        """
        return self.width * self.height
