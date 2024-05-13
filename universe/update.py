import enum
from typing import Any, Dict, Optional


class UpdateType(enum.Enum):
    UNKNOWN = -1
    SIMULATION_START = 0
    SIMULATION_END = 1
    SIMULATION_PAUSE = 2
    SIMULATION_RESUME = 3
    SIMULATION_TPS = 4
    SIMULATION_SET_TPS = 5

    ANT_SPAWN = 10
    ANT_MOVE = 11
    ANT_DEATH = 12
    ANT_ATTACK = 13
    ANT_PROMOTE = 14

    NEST_SPAWN = 20

    OBJECT_SPAWN = 30
    OBJECT_DESPAWN = 31


class Update:
    """
    Class representing an update in the simulation.

    Attributes:
        type (UpdateType): The type of the update.
        ant (Optional[Ant]): The ant involved in the update, if any.
        target (Optional[Any]): The target of the update, if any.
    """

    type: UpdateType = UpdateType.UNKNOWN
    ant: Optional["Ant"] = None
    target: Optional[Any] = None

    def __init__(
        self,
        _type: UpdateType,
        ant: Optional["Ant"] = None,
        target: Optional[Any] = None,
        state: Optional[Any] = None,
    ):
        """
        Initialize an Update instance.

        Args:
            _type (UpdateType): The type of the update.
            ant (Optional[Ant]): The ant involved in the update, if any.
            target (Optional[Any]): The target of the update, if any.
            state (Optional[Any]): The state of the update, if any.
        """
        self.type = _type
        self.ant = ant
        self.target = target
        self.state = state

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the update to a dictionary.

        Returns:
            dict: A dictionary representation of the update.
        """
        return {
            "type": self.type.name,
            "ant": self.ant.to_dict() if self.ant else None,
            "target": self.target.to_dict() if self.target else None,
            "state": self.state,
        }
