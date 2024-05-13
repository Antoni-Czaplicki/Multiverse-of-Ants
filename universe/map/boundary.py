class Boundary:
    x: int = 0
    y: int = 0
    width: int = 200
    height: int = 200

    @staticmethod
    def set_boundary(x: int, y: int, width: int, height: int) -> None:
        """
        Set the boundary with the given x, y, width, and height.

        :param x: The x-coordinate of the boundary.
        :param y: The y-coordinate of the boundary.
        :param width: The width of the boundary.
        :param height: The height of the boundary.
        """
        Boundary.x = x
        Boundary.y = y
        Boundary.width = width
        Boundary.height = height

    @staticmethod
    def set_boundary_by_size(size: int) -> None:
        """
        Set the boundary by size. The x and y coordinates are set to negative half of the size,
        and the width and height are set to the size.

        :param size: The size to set the boundary.
        """
        Boundary.x = 0
        Boundary.y = 0
        Boundary.width = size
        Boundary.height = size

    @staticmethod
    def contains(position) -> bool:
        """
        Check if the given position is within the boundary.

        :param position: The position to check.
        :return: True if the position is within the boundary, False otherwise.
        """
        return (
            Boundary.x <= position.x <= Boundary.x + Boundary.width
            and Boundary.y <= position.y <= Boundary.y + Boundary.height
        )
