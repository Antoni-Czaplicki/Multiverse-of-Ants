import enum


class UpdateType(enum.Enum):
    UNKNOWN = -1

    SIMULATION_START = 0
    SIMULATION_END = 1
    SIMULATION_PAUSE = 2
    SIMULATION_RESUME = 3
    SIMULATION_TPS = 4

    ANT_SPAWN = 10
    ANT_MOVE = 11
    ANT_DEATH = 12
    ANT_ATTACK = 13
    ANT_PROMOTE = 14


class Update:
    type: UpdateType = UpdateType.UNKNOWN
    ant: "Ant" = None
    target = None

    def __init__(self, _type: UpdateType, ant: "Ant" = None, target=None, state=None):
        self.type = _type
        self.ant = ant
        self.target = target
        self.state = state

    def to_dict(self):
        return {
            "type": self.type.name,
            "ant": self.ant.to_dict() if self.ant else None,
            "target": self.target.to_dict() if self.target else None,
            "state": self.state,
        }
