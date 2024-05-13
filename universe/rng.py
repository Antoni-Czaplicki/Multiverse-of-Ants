import random


class RNG:
    """A class to handle random number generation."""

    seed = 0

    @staticmethod
    def set_seed(seed: int) -> None:
        """
        Set the seed for the random number generator.

        :param seed: The seed to set.
        """
        RNG.seed = seed
        random.seed(seed)

    @staticmethod
    def set_random_seed() -> int:
        """
        Set a random seed for the random number generator.

        :return: The seed that was set.
        """
        RNG.set_seed((RNG.seed * 1103515245 + 12345) & 0x7FFFFFFF)
        return RNG.seed

    @staticmethod
    def random() -> float:
        """
        Generate a random float between 0 and 1.

        :return: A random float.
        """
        return random.random()

    @staticmethod
    def randint(a: int, b: int) -> int:
        """
        Generate a random integer between a and b.

        :param a: The lower bound.
        :param b: The upper bound.
        :return: A random integer.
        """
        return random.randint(a, b)

    @staticmethod
    def choice(seq: list) -> any:
        """
        Choose a random element from a sequence.

        :param seq: The sequence to choose from.
        :return: A random element from the sequence.
        """
        return random.choice(seq)
