from collections import defaultdict
from typing import Dict, List, Tuple

from .ants import Ant
from .map import Boundary, Nest, Object
from .rng import RNG


class Universe:
    """
    Class representing the universe.

    The universe is the environment in which the simulation takes place.

    :var rng: The random number generator.
    :type rng: RNG
    :var boundary: The boundary of the universe.
    :type boundary: Boundary
    :var ants: A dictionary of ants.
    :type ants: Dict[Tuple[int, int], List[Ant]]
    :var objects: A dictionary of objects.
    :type objects: Dict[Tuple[int, int], List[Object]]
    :var nests: A list of nests.
    :type nests: List[Nest]
    """

    rng: RNG
    boundary: Boundary
    ants: Dict[Tuple[int, int], List[Ant]]
    objects: Dict[Tuple[int, int], List[Object]]
    nests: List[Nest]

    MAX_ANTS = 500
    MAX_OBJECTS = 500
    ants_count = 0
    objects_count = 0

    def __init__(self):
        """Initialize the universe."""
        self.rng = RNG()
        self.boundary = Boundary()
        self.ants = defaultdict(list)
        self.objects = defaultdict(list)
        self.nests = []
