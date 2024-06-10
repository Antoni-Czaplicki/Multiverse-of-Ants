import random
from typing import Any


class RNG:
    """A class to handle random number generation."""

    seed = 0
    random_instance = None

    def set_seed(self, seed: Any) -> None:
        """
        Set the seed for the random number generator.

        :param seed: The seed to set.
        :type seed: Any
        """
        self.seed = seed
        self.random_instance = random.Random(seed)

    def set_random_seed(self) -> int:
        """
        Set a random seed for the random number generator.

        :return: The seed that was set.
        :rtype: int
        """
        self.set_seed((RNG.seed * 1103515245 + 12345) & 0x7FFFFFFF)
        return self.seed

    def random(self) -> float:
        """
        Generate a random float between 0 and 1.

        :return: A random float.
        :rtype: float
        """
        return self.random_instance.random()

    def randint(self, a: int, b: int) -> int:
        """
        Generate a random integer between a and b.

        :param a: The lower bound.
        :type a: int
        :param b: The upper bound.
        :type b: int
        :return: A random integer.
        :rtype: int
        """
        return self.random_instance.randint(a, b)

    def choice(self, seq: list) -> any:
        """
        Choose a random element from a sequence.

        :param seq: The sequence to choose from.
        :type seq: list
        :return: A random element from the sequence.
        :rtype: any
        """
        return self.random_instance.choice(seq)
