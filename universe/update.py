import enum
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from universe.ants import Ant


class UpdateType(enum.Enum):
    """Enum class for update types."""

    UNKNOWN = -1
    SIMULATION_START = 0
    SIMULATION_END = 1
    SIMULATION_PAUSE = 2
    SIMULATION_RESUME = 3
    SIMULATION_TPS = 4
    SIMULATION_SET_TPS = 5
    SIMULATION_SET_BOUNDARIES = 6
    SIMULATION_SET_SEED = 7
    SIMULATION_SET_ROUNDS = 8
    SIMULATION_CURRENT_ROUND = 9

    ANT_SPAWN = 10
    ANT_MOVE = 11
    ANT_DEATH = 12
    ANT_ATTACK = 13
    ANT_PROMOTE = 14

    NEST_SPAWN = 20

    OBJECT_SPAWN = 30
    OBJECT_DESPAWN = 31

    ERROR_INVALID_TPS = 40
    ERROR_INVALID_ROUNDS = 41
    ERROR_SIMULATION_NOT_RUNNING = 42


class Update:
    """
    Class representing an update in the simulation.
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

        :param _type: The type of the update.
        :type _type: UpdateType
        :param ant: The ant involved in the update.
        :type ant: Optional[Ant]
        :param target: The target of the update.
        :type target: Optional[Any]
        :param state: The state of the update.
        :type state: Optional[Any]
        """
        self.type = _type
        self.ant = ant
        self.target = target
        self.state = state

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the update to a dictionary.

        :return: The dictionary representation of the update.
        """
        return {
            "type": self.type.name,
            "ant": self.ant.to_dict() if self.ant else None,
            "target": self.target.to_dict() if self.target else None,
            "state": self.state,
        }
