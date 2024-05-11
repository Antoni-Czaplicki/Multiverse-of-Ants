class Boundary:
    x = -100
    y = -100
    width = 200
    height = 200

    @staticmethod
    def set_boundary(x, y, width, height):
        Boundary.x = x
        Boundary.y = y
        Boundary.width = width
        Boundary.height = height

    @staticmethod
    def set_boundary_by_size(size):
        Boundary.x = -size // 2
        Boundary.y = -size // 2
        Boundary.width = size
        Boundary.height = size

    @staticmethod
    def contains(position):
        return (
            Boundary.x <= position.x <= Boundary.x + Boundary.width
            and Boundary.y <= position.y <= Boundary.y + Boundary.height
        )
