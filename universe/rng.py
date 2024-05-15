import random


class RNG:
    """A class to handle random number generation."""

    seed = 0
    random_instance = None

    def set_seed(self, seed: int) -> None:
        """
        Set the seed for the random number generator.

        :param seed: The seed to set.
        """
        self.seed = seed
        self.random_instance = random.Random(seed)

    def set_random_seed(self) -> int:
        """
        Set a random seed for the random number generator.

        :return: The seed that was set.
        """
        self.set_seed((RNG.seed * 1103515245 + 12345) & 0x7FFFFFFF)
        return self.seed

    def random(self) -> float:
        """
        Generate a random float between 0 and 1.

        :return: A random float.
        """
        return self.random_instance.random()

    def randint(self, a: int, b: int) -> int:
        """
        Generate a random integer between a and b.

        :param a: The lower bound.
        :param b: The upper bound.
        :return: A random integer.
        """
        return self.random_instance.randint(a, b)

    def choice(self, seq: list) -> any:
        """
        Choose a random element from a sequence.

        :param seq: The sequence to choose from.
        :return: A random element from the sequence.
        """
        return self.random_instance.choice(seq)
