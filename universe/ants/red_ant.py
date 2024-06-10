from typing import TYPE_CHECKING, Callable

from ..map import ObjectType
from ..update import UpdateType
from .ant import Ant, Role

if TYPE_CHECKING:
    from universe.universe import Universe


class RedAnt(Ant):
    """
    RedAnt is a subclass of Ant with specific attributes.
    It has a health of 40, damage of 15, and speed of 4.
    """

    health: int = 40
    damage: int = 15
    speed: int = 4

    async def move(
        self,
        universe: "Universe",
        update_callback: Callable,
    ) -> None:
        """
        Move the red ant in the universe.
        
        :param universe: The universe.
        :type universe: Universe
        :param update_callback: The callback function to update the state.
        :type update_callback: Callable
        """
        available_directions = self.available_directions(universe.boundary)
        if available_directions:
            # Combine direction and distance into a single choice
            direction_distance = [
                {
                    "direction": universe.rng.choice(available_directions),
                    "distance": universe.rng.randint(0, self.speed),
                }
            ]

            entity_position_neighbours = self.position.get_neighbors(self.speed)

            ant_positions = [
                {"new_position": position}
                for position in entity_position_neighbours
                if (
                    (position.x, position.y) in universe.ants
                    and any(
                        type(ant) is not type(self)
                        for ant in universe.ants[(position.x, position.y)]
                    )
                )
            ]

            object_positions = [
                {"new_position": position}
                for position in entity_position_neighbours
                if (
                    (position.x, position.y) in universe.objects
                    and universe.objects[(position.x, position.y)]
                    and universe.objects[(position.x, position.y)][0].object_type
                    is not ObjectType.ROCK
                )
            ]

            proposed_positions = (
                ant_positions * 2 + object_positions
            )  # Double the weight of ant_positions

            if self.role == Role.QUEEN:
                nearest_nest = min(
                    universe.nests,
                    key=lambda nest: nest.area.smallest_distance(self.position),
                )
                direction_to_nest = nearest_nest.area.direction_from_position(
                    self.position
                )
                if (
                    direction_to_nest is not None
                    and self.position not in nearest_nest.area
                ):
                    distance_to_nest = nearest_nest.area.smallest_distance(
                        self.position
                    )
                    direction_distance.extend(
                        [
                            {
                                "direction": direction_to_nest,
                                "distance": min(abs(distance_to_nest), self.speed),
                            }
                            for _ in range(6)
                        ]
                    )  # Add 6 more moves towards the nest to increase the chance of moving towards the nest for the red queen
            chosen_move = universe.rng.choice(
                direction_distance + proposed_positions * 2
            )  # Double the weight of proposed_positions
            self.position.move(universe.boundary, **chosen_move)
            if self.food > 0:
                self.food -= 1
            else:
                self.health -= 1
                if self.health <= 0:
                    await self.die(update_callback)
                    return  # When the ant dies, it should not move
            await update_callback(UpdateType.ANT_MOVE, self)
