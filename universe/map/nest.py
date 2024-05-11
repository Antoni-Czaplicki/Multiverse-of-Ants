from area import Area
from position import Position

from universe.ants import Ant


class Nest:
    ants_per_unit_area = 5
    queen: Ant = None

    def __init__(self, area: Area):
        self.area = area

    def __contains__(self, position: Position):
        return position in self.area

    def ants_type(self):
        return type(self.queen)
