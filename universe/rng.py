import random


class RNG:
    seed = 0

    @staticmethod
    def set_seed(seed):
        RNG.seed = seed
        random.seed(seed)

    @staticmethod
    def set_random_seed():
        RNG.set_seed((RNG.seed * 1103515245 + 12345) & 0x7FFFFFFF)
        return RNG.seed

    @staticmethod
    def random():
        return random.random()

    @staticmethod
    def randint(a, b):
        return random.randint(a, b)

    @staticmethod
    def choice(seq):
        return random.choice(seq)
