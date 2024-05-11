from position import Position


class Area:
    def __init__(self, position1: Position, position2: Position):
        self.position1 = position1
        self.position2 = position2

    def __contains__(self, position: Position):
        return (
            self.position1.x <= position.x <= self.position2.x
            and self.position1.y <= position.y <= self.position2.y
        )

    def __str__(self):
        return f"({self.position1}, {self.position2})"

    def __repr__(self):
        return f"Area({self.position1}, {self.position2})"

    def size(self):
        return (self.position2 - self.position1).manhattan_distance(Position(0, 0))
