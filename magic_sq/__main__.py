import logging
import sys
import time

from argparse import ArgumentParser
from itertools import count
from multiprocessing import Pool

logger = logging.getLogger(__name__)


try:
    from . import test
    from .generate_factors import GenerateFactorings
except ImportError:
    from magic_sq import test
    from magic_sq.generate_factors import GenerateFactorings


class GenerateFactoringsMgSqSq(GenerateFactorings):
    """
    A modified version of GenerateFactorings.
        Skips all factorings that will not lead to at least 4 x**2+y**2 combinations,
        and are not relevant to the problem.
    """

    def __init__(self):
        super().__init__()

        self.two_max = 1
        self.P = dict()
        self.Q = dict()

    def next(self):
        base, i, val = super().next()

        if base == 2:
            self.two_max = i
            t = '2'
        elif base % 4 == 1:
            self.P[base] = i
            t = 'P'
        else:
            self.Q[base] = i
            t = 'Q'

        return base, i, val, t

    def _get_numbers(self, two_max, p_factorings_max, q_factorings_max):

        if two_max:
            target_key = 2
            target_key_max = two_max
            for combo in self._get_numbers(0, p_factorings_max, q_factorings_max):
                for e in range(0, target_key_max + 1):
                    yield combo | {target_key: e}

        elif p_factorings_max:
            target_key = max(p_factorings_max)
            target_key_max = p_factorings_max[target_key]
            p_factorings_max = {k: v for k, v in p_factorings_max.items() if k != target_key}

            for combo in self._get_numbers(two_max, p_factorings_max, q_factorings_max):
                for e in range(0, target_key_max + 1):
                    yield combo | {target_key: e}

        elif q_factorings_max:
            target_key = max(q_factorings_max)
            target_key_max = q_factorings_max[target_key]
            q_factorings_max = {k: v for k, v in q_factorings_max.items() if k != target_key}

            for combo in self._get_numbers(two_max, p_factorings_max, q_factorings_max):
                for e in range(0, target_key_max + 1, 2):
                    yield combo | {target_key: e}

        else:
            yield dict()
            return

    def get_numbers(self, target_P, target_Q, cur_base, cur_i):
        # We have the value for our current base, so that is not needed
        for combo in self._get_numbers(self.two_max if cur_base != 2 else 0, target_P, target_Q):
            yield combo | {cur_base: cur_i}

    def get_factorings(self):
        while True:
            cur_base, cur_i, cur_val, t = self.next()

            if t == 'Q' and cur_i % 2 == 1:
                continue

            target_P = self.P if t != 'P' else {k: v for k, v in self.P.items() if k != cur_base}
            target_Q = self.Q if t != 'Q' else {k: v for k, v in self.Q.items() if k != cur_base}
            for combo in self.get_numbers(target_P, target_Q, cur_base, cur_i):
                combo = {k: v for k, v in combo.items() if v != 0}
                if combo:
                    yield combo


def multithreaded_test(i):
    """Wrapper for ThreadPool"""
    return test(i, limited_checks=True)


def main(n=None, start=2, multiprocessing=True, targeted_generation=False):
    """
    Search for a magic square of squares (bimagic square of order 3)

    For this code, the model of the problem is as follows:
        a**2 b**2 c**2
        d**2 e**2 f**2
        g**2 h**2 i**2

    To start to understand this, first lets build a list of equations that 
        are used in this problem:

    a**2 + b**2 + c**2 = k
    d**2 + e**2 + f**2 = k
    g**2 + h**2 + i**2 = k
    a**2 + d**2 + g**2 = k
    b**2 + e**2 + h**2 = k
    c**2 + f**2 + i**2 = k
    a**2 + e**2 + i**2 = k
    c**2 + e**2 + g**2 = k

    Looking at this I first noted that you could set a**2 + b**2 + c**2 = a**2 + d**2 + g**2 (or some rotation),
        and remove the a**2 to get b**2 + c**2 = d**2 + g**2

    It stood out to me that the essence of solving this algorithm could be finding co-equal pairs of numbers that
        satisfy this equality. 

    Then the problem becomes, how do I take 2 pairs of solutions and join them together into the outside and inside
        areas. However it quickly stood out that the best way to join them up would be not to visualize joining them
        on the outside areas, but instead join them in the middle using `e` since that is the most important variable
        (it is used in the most equations above).

    So: If I could find 4 total solutions to x**2 + y**2 that are all unique and equal, then I can arrange them such as
        pairs: (a1, a2), (b1, b2), (c1, c2), (d1, d2)

        a1**2 b1**2 c1**2
        d1**2 e**2  d2**2
        c2**2 b2**2 a2**2

    Doing this method, I can take the 4 directions:
        a1**2 + e**2 + a2**2 (diagonal)
        c1**2 + e**2 + c2**2 (diagonal)
        b1**2 + e**2 + b2**2 (center)
        d1**2 + e**2 + d2**2 (middle)

    and be guarenteed they are all already equal for any value of e. Halfway there...

    Futhermore, we can compute an e using the top row by doing `e = sqrt((a1**2 + b1**2 + c1**2) - (d1**2 + d2**2))`
        This will also ensure that the top row's value (a**2 + b**2 + c**2 above) will match the above 4 values

    The next step is simply to verify the remaining 3 directions for any potential solutions. They are:
        a**2 + d**2 + g**2 (left column)
        c**2 + f**2 + i**2 (right column)
        g**2 + h**2 + i**2 (bottom row)

    I have only added a check for the bottom row however, and to date,
        no potential solutions have made it passed that point...
    """
    if targeted_generation:
        iterator = GenerateFactoringsMgSqSq()
        log_step = 10**2
    else:
        iterator = count(start) if n is None else range(start, n)
        log_step = 10**5

    if multiprocessing:
        with Pool() as tp:
            for i, ans in enumerate(tp.imap(test if not targeted_generation else multithreaded_test,
                                            iterator,
                                            chunksize=10**4),
                                    start=start):
                if ans:
                    logger.critical('ANSWER: %s', ans)
                    break

                if i % log_step == 0:
                    logger.info('Passing %s', i)

                if targeted_generation and n and i == n:
                    break
    else:
        for i, ans in enumerate(iterator):
            test(i, limited_checks=not targeted_generation)

            if ans:
                logger.critical('ANSWER: %s', ans)
                break

            if i % log_step == 0:
                logger.info('Passing %s', i)

            if targeted_generation and n and i == n:
                break


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('end', type=int, default=None, nargs='?')
    parser.add_argument('--start', type=int, default=2, 
                        help="The start point. Be VERY careful to start well below the last end point, "
                             "or a solution may be missed.")
    parser.add_argument('--targeted', action='store_true', default=False,
                        help="Generate factorizations instead of factoring all numbers. "
                             "This is faster, and eventually all numbers should be generated... "
                             "but vastly out of order")

    args = parser.parse_args()

    _stream = logging.StreamHandler(sys.stdout)
    _stream.setLevel(logging.INFO)
    _stream.setFormatter(logging.Formatter('%(message)s'))
    _file = logging.FileHandler('the.log')
    _file.setLevel(logging.DEBUG)
    _file.setFormatter(logging.Formatter('%(module)s::%(funcName)s::%(lineno)d %(levelname)s %(asctime)s - %(message)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_stream)
    logger.addHandler(_file)

    logger.info('Starting with end=%s at start=%s', args.end, args.start)
    start_time = time.time()
    main(args.end, args.start, targeted_generation=args.targeted)
    end_time = time.time()
    logger.info('Took %s', end_time - start_time)
