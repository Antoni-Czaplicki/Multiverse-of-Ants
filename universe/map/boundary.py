class Boundary:
    x: int = 0
    y: int = 0
    width: int = 200
    height: int = 200

    def set_boundary(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set the boundary with the given x, y, width, and height.

        :param x: The x-coordinate of the boundary.
        :param y: The y-coordinate of the boundary.
        :param width: The width of the boundary.
        :param height: The height of the boundary.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set_boundary_by_width_height(self, width: int, height: int) -> None:
        """
        Set the boundary by width and height. The x and y coordinates are set to zero.

        :param width: The width of the boundary.
        :param height: The height of the boundary.
        """
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def set_boundary_by_size(self, size: int) -> None:
        """
        Set the boundary by size. The x and y coordinates are set to negative half of the size,
        and the width and height are set to the size.

        :param size: The size to set the boundary.
        """
        self.x = 0
        self.y = 0
        self.width = size
        self.height = size

    def contains(self, position) -> bool:
        """
        Check if the given position is within the boundary.

        :param position: The position to check.
        :return: True if the position is within the boundary, False otherwise.
        """
        return (
            self.x <= position.x <= self.x + self.width
            and self.y <= position.y <= self.y + self.height
        )

    def size(self) -> int:
        """
        Get the size of the boundary.

        :return: The size of the boundary.
        """
        return self.width * self.height
