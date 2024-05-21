from collections import defaultdict
from typing import Dict, List, Tuple

from .ants import Ant
from .map.boundary import Boundary
from .map.nest import Nest
from .map.object import Object
from .rng import RNG


class Universe:
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
        self.rng = RNG()
        self.boundary = Boundary()
        self.ants = defaultdict(list)
        self.objects = defaultdict(list)
        self.nests = []
