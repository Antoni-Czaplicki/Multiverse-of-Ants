import unittest
from unittest.mock import AsyncMock
from universe.engine import run
import asyncio
from universe.universe import Universe

class TestRunFunction(unittest.TestCase):
    def setUp(self):
        self.update_callback = AsyncMock()
        self.universe = Universe()
        self.first_results = {}

    async def test_run_function_returns_same_value_for_set_seed(self):
        seed = 1532  # Choosing a seed you want to test
        self.universe.rng.set_seed(seed)
        config = {"seed": seed}
        result = asyncio.run(run(config, self.update_callback))

        if seed not in self.first_results:
            self.first_results[seed] = result
        else:
            # Comparing the current result with the first result for this seed
            if self.first_results[seed] == result:
                print('OK')
            else:
                print('The result for seed {} is different in different runs of the simulation'.format(seed))
        return None

if __name__ == '__main__':
    unittest.main()