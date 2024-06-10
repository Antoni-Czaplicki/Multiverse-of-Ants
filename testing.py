import random
import unittest
from unittest.mock import AsyncMock

from universe.engine import run


class TestRunFunction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.update_callback = AsyncMock()
        self.first_results = {}

    async def test_run_function_returns_same_value_for_set_seed(self):
        seeds = [random.randint(0, 1000) for _ in range(5)]
        for seed in seeds:
            print(f"Running simulation with seed {seed}...")
            self.first_results[seed] = await run(
                {"seed": seed, "rounds": 50}, self.update_callback
            )

        for seed in seeds:
            print(f"Running simulation with seed {seed} again...")
            result = await run({"seed": seed, "rounds": 50}, self.update_callback)
            self.compare_results(seed, result)

    def compare_results(self, seed, result):
        if self.first_results[seed] == result:
            print("OK")
        else:
            print(
                f"The result for seed {seed} is different in different runs of the simulation"
            )
            print(f"First result: {self.first_results[seed]}")
            print(f"Second result: {result}")
            self.assertEqual(self.first_results[seed], result)


if __name__ == "__main__":
    unittest.main()
