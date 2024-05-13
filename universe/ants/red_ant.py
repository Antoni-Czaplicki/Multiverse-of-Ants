from .ant import Ant


class RedAnt(Ant):
    """
    RedAnt is a subclass of Ant with specific attributes.
    It has a health of 40, damage of 15, and speed of 4.
    """

    health: int = 40
    damage: int = 15
    speed: int = 4
