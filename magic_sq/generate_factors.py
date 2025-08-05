from itertools import count

from sympy.ntheory.generate import nextprime


class GenerateFactorings:
    """
    A class to iterate over all numbers using primes to generate all factorizations

    Attributes:
        generators (dict): A dictionary used to store methods which are generating the future exponent to be used.
        factorings (dict): A dictionary used to track the current max exponents for each base.
        next_factorings (dict): A dictionary used to store the next exponents and values, which can be searched.
    """

    def __init__(self):
        self.generators = dict()
        self.factorings = dict()
        self.next_factorings = {2: next(self.generator(2))}

    def generator(self, base):
        """Returns a generator that yields the next exponent and value for a given base, backed by a cache"""
        if base not in self.generators:
            self.generators[base] = iter((i, base**i) for i in count(1))
            
        return self.generators[base]

    def next(self):
        """
        Returns the next base, i, and value for the next factorization combination
            The goal is to select the next smallest value for combination, so that numbers are generated relatively
            in order.
        """
        base, (i, val) = min(self.next_factorings.items(), key=lambda k: k[1][1])

        # Setup the next value for this base
        self.next_factorings[base] = next(self.generator(base))

        if base == max(self.next_factorings):
            # The base is the largest prime in the next_factorings dict, so we need a new largest prime too
            next_prime = nextprime(base)
            self.next_factorings[next_prime] = next(self.generator(next_prime))

        self.factorings[base] = i
        return base, i, val

    def _get_numbers(self, factorings_max):
        """
        Creates a generator that yields all possible combinations of exponents

        Args:
            factorings_max (dict): A dictionary where the keys are bases and the values are the maximum possible
                values for the exponents
        """
        if not factorings_max:
            yield dict()
            return

        target_key = max(factorings_max)    
        for combo in self._get_numbers({k: v for k, v in factorings_max.items() if k != target_key}):
            for e in range(0, factorings_max[target_key] + 1, 1):
                yield combo | {target_key: e}

    def get_numbers(self, target_bases, cur_base, cur_i):
        """Wrapper to add the current base and exponent to the target_bases dict"""
        # We have the value for our current base, so that is not needed
        for combo in self._get_numbers(dict(target_bases)):
            yield combo | {cur_base: cur_i}

    def get_factorings(self):
        """Yields all possible factorings"""
        while True:
            cur_base, cur_i, cur_val = self.next()
            target_bases = {k: v for k, v in self.factorings.items() if k != cur_base}
            for combo in self.get_numbers(target_bases, cur_base, cur_i):
                combo = {k: v for k, v in combo.items() if v != 0}
                if combo:
                    yield combo

    def __iter__(self):
        return self.get_factorings()
